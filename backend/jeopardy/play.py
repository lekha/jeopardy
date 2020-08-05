import inspect
from typing import Collection
from typing import Optional

from jeopardy import exceptions
from jeopardy.models.action import ActionOrmModel
from jeopardy.models.action import ActionType
from jeopardy.models.action import NoAction
from jeopardy.models.action import ResponseOrm
from jeopardy.models.action import WagerOrm
from jeopardy.models.game import GameOrm
from jeopardy.models.game import GameStatus
from jeopardy.models.game import RoundClass
from jeopardy.models.game import RoundOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.reveals import BoardLevel
from jeopardy.models.reveals import BoardLevelDetail
from jeopardy.models.reveals import RoundRevealOrm
from jeopardy.models.team import TeamOrm
from jeopardy.models.user import UserOrm
from jeopardy.parse import action_orm_from_type
from jeopardy.parse import parse_game_code
from jeopardy.schema.action import Action
from jeopardy.validation import is_round_over
from jeopardy.validation import is_valid_game_code


async def game_from_code(raw_game_code: str) -> GameOrm:
    """Validate the input code and retrieve the associated GameOrm."""
    if not is_valid_game_code(raw_game_code):
        raise exceptions.ForbiddenAccessException

    game_code = parse_game_code(raw_game_code)
    game = await GameOrm.get_or_none(code=game_code)

    if game is None:
        raise exceptions.ForbiddenAccessException

    return game


async def start(game: GameOrm) -> None:
    """Create teams and allow users to start joining a game."""
    game.status = GameStatus.JOINABLE
    await game.save()

    team_names = ["Elf", "Goblin", "Ogre", "Troll", "Wizard"]
    for i in range(game.max_teams):
        await TeamOrm.create(game=game, name=f"Team {team_names[i]}")


async def next_round_action_type(
    prev_action: ActionOrmModel
) -> Optional[ActionType]:
    """Determine actions that are permitted next in the round."""
    basic_round_mapping = {
        None:                ActionType.CHOICE,
        ActionType.BUZZ:     ActionType.RESPONSE,
        ActionType.CHOICE:   _buzz_or_wager,
        ActionType.RESPONSE: _buzz_or_choice_if_tiles_available,
        ActionType.WAGER:    ActionType.RESPONSE,
    }
    final_round_mapping = {
        None:                ActionType.WAGER,
        ActionType.RESPONSE: _collect_responses,
        ActionType.WAGER:    _collect_wagers,
    }

    round_ = await prev_action.round_
    if round_.class_ == RoundClass.FINAL:
        next_action_type_mapping = final_round_mapping
    else:
        next_action_type_mapping = basic_round_mapping

    func_or_const = next_action_type_mapping[prev_action.type_]
    if inspect.iscoroutinefunction(func_or_const):
        next_action_type = await func_or_const(prev_action)
    else:
        next_action_type = func_or_const

    return next_action_type


async def _buzz_or_wager(prev_action: ActionOrmModel) -> ActionType:
    """Helper for determining next action type."""
    await prev_action.fetch_related("tile")
    if prev_action.tile.is_daily_double:
        next_action_type = ActionType.WAGER
    else:
        next_action_type = ActionType.BUZZ
    return next_action_type


async def _buzz_or_choice_if_tiles_available(
    prev_action: ResponseOrm
) -> ActionType:
    """Helper for determining next action type."""
    if await _all_teams_have_response(prev_action):
        tiles_available = (
            await TileOrm
            .filter(category__board__round_=await prev_action.round_)
            .filter(choices__id=None)
            .count()
        )
        if tiles_available:
            next_action_type = ActionType.CHOICE
        else:
            next_action_type = NoAction(await prev_action.round_)

    elif prev_action.is_correct:
        next_action_type = ActionType.CHOICE

    else:
        next_action_type = ActionType.BUZZ

    return next_action_type


async def _collect_responses(prev_action: ActionOrmModel) -> ActionType:
    """Helper for determining next action type."""
    await prev_action.fetch_related("game__teams")
    await prev_action.fetch_related("tile__responses")
    if await _all_teams_have_response(prev_action):
        next_action_type = NoAction(await prev_action.round_)
    else:
        next_action_type = ActionType.RESPONSE
    return next_action_type


async def _all_teams_have_response(prev_action: ActionOrmModel) -> bool:
    """Helper for determining next action type."""
    await prev_action.fetch_related("game__teams")
    await prev_action.fetch_related("tile__responses")
    return len(prev_action.game.teams) == len(prev_action.tile.responses)


async def _collect_wagers(prev_action: ActionOrmModel) -> ActionType:
    """Helper for determining next action type."""
    await prev_action.fetch_related("game__teams")
    await prev_action.fetch_related("tile__wagers")
    if len(prev_action.game.teams) != len(prev_action.tile.wagers):
        next_action_type = ActionType.WAGER
    else:
        next_action_type = ActionType.RESPONSE
    return next_action_type


async def perform(game: GameOrm, player: UserOrm, action: Action):
    """Update the game by performing the action."""
    # Store action in database
    action_orm = await _save_action_in_database(game, player, action)

    # Update state to reveal more information
    round_ = await game.next_round
    for detail in _detail_revealed(action.type_, action.tile.is_daily_double):
        await RoundRevealOrm.create(
            round_=round_,
            level=BoardLevel.TILE,
            level_id=action.tile.id,
            detail=detail,
        )

    # Update next_chooser, next_round, and team score
    if action.type_ == ActionType.RESPONSE:
        team = await player.team(game)
        tile_value = await _tile_value(game, team, action.tile)

        if action_orm.is_correct:
            game.next_chooser = team
            team.score += tile_value
        else:
            team.score -= tile_value
        await team.save()

        if await is_round_over(round_):
            game.next_round = await _next_round(round_)

            # New round means lowest-scoring team gets to choose
            teams = await game.teams
            teams.sort(key=lambda x: x.score)
            lowest_scoring_team = teams[0]
            game.next_chooser = lowest_scoring_team

    # Update next_action_type
    next_action_type = await next_round_action_type(action_orm)
    if all((
        game.next_round is not None,             # game isn't over, but
        game.next_round != round_,               # round has changed
        isinstance(next_action_type, NoAction),  # because last round ended
    )):
        next_action_type = await next_round_action_type(next_action_type)
    if isinstance(next_action_type, NoAction):   # game is over
        next_action_type = None
    game.next_action_type = next_action_type

    # Update next_message_id
    game.next_message_id += 1

    await game.save()


def _detail_revealed(
    action_type: ActionType, is_daily_double: bool
) -> Collection[BoardLevelDetail]:
    """Helper for perform."""
    details = set()
    if action_type == ActionType.CHOICE:
        details.add(BoardLevelDetail.IS_DAILY_DOUBLE)
        if not is_daily_double:
            details.add(BoardLevelDetail.ANSWER)

    elif action_type == ActionType.WAGER:
        details.add(BoardLevelDetail.ANSWER)

    elif action_type == ActionType.RESPONSE:
        details.add(BoardLevelDetail.QUESTION)

    return details


async def _next_round(round_: RoundOrm) -> Optional[RoundOrm]:
    """Helper for perform."""
    game = await round_.game
    all_rounds = await game.rounds

    all_rounds.sort(key=lambda x: x.ordinal)
    all_rounds.append(None)

    for i, i_round in enumerate(all_rounds):
        if i_round.id == round_.id:
            break

    return all_rounds[i+1]


async def _save_action_in_database(
    game: GameOrm, player: UserOrm, action: Action
) -> ActionOrmModel:
    """Helper for perform."""
    action_orm_class = action_orm_from_type(action.type_)
    tile = await action.tile
    team = await player.team(game)

    if action.type_ == ActionType.RESPONSE:
        # TODO: Separate into an is_correct(response) function in validation.py
        is_correct = (await tile.trivia).question == action.question
        action_orm = await action_orm_class.create(
            game=game, tile=tile, team=team, user=player, is_correct=is_correct
        )
    elif action.type_ == ActionType.WAGER:
        action_orm = await action_orm_class.create(
            game=game, tile=tile, team=team, user=player, amount=action.amount
        )
    else:
        action_orm = await action_orm_class.create(
            game=game, tile=tile, team=team, user=player
        )

    return action_orm


async def _tile_value(game: GameOrm, team: TeamOrm, tile: TileOrm) -> int:
    """Helper for perform."""
    round_ = await tile.round_
    # Daily double tile or final jeopardy round
    if tile.is_daily_double or round_.class_ == RoundClass.FINAL:
        wager = await WagerOrm.get(team=team, tile=tile, game=game)
        value = wager.amount

    # Normal tile in single or double jeopardy round
    else:
        if round_.class_ == RoundClass.SINGLE:
            multiplier = 200
        elif round_.class_ == RoundClass.DOUBLE:
            multiplier = 400

        await tile.fetch_related("category__tiles")
        category_tiles = list(tile.category.tiles)
        category_tiles.sort(key=lambda x: x.ordinal)
        for position, category_tile in enumerate(category_tiles):
            if category_tile.id == tile.id:
                break
        value = multiplier * (position + 1)

    return value
