import random
import string

from jeopardy import state
from jeopardy.models.game import BoardOrm
from jeopardy.models.game import CategoryOrm
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.models.game import RoundOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.game import TriviaOrm
from jeopardy.models.user import UserOrm
from jeopardy.schema.state import Game


async def new_game_code() -> str:
    """Generate a game code that hasn't been used before."""
    code = "".join(random.choice(string.ascii_uppercase) for _ in range(4))
    is_in_use = await GameOrm.get_or_none(code=code) is not None
    while is_in_use:
        code = "".join(random.choice(string.ascii_uppercase) for _ in range(4))
        is_in_use = await GameOrm.get_or_none(code=code) is not None
    return code


async def game(
    owner: UserOrm, *, name: str, max_teams: int, max_players_per_team: int,
) -> Game:
    """Create a new game."""
    game_orm = await GameOrm.create(
        name=name,
        code=await new_game_code(),
        owner=owner,
        max_teams=max_teams,
        max_players_per_team=max_players_per_team,
        next_message_id=0,
        is_started=False,
        is_finished=False,
    )

    # Pre-create a board for the time being. To be removed later.
    round_ = await RoundOrm.create(
        game=game_orm, class_=RoundClass.SINGLE, ordinal=0
    )
    game_orm.next_round = round_
    await game_orm.save()

    board = await BoardOrm.create(round_=round_)
    for i in range(board.num_categories):
        category = await CategoryOrm.create(
            board=board, name=f"Category {i}", ordinal=i
        )
        for j in range(board.num_tiles_per_category):
            trivia = await TriviaOrm.create(
                answer="Answer", question="Question?"
            )
            await TileOrm.create(category=category, trivia=trivia, ordinal=j)

    return await state.full(game_orm.code)
