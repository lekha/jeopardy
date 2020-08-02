from unittest.mock import patch

import pytest

from jeopardy.play import next_round_action_type
from jeopardy.play import perform
from jeopardy.models.action import ActionType
from jeopardy.models.action import NoAction
from jeopardy.models.game import GameOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.team import TeamOrm
from jeopardy.schema.action import Response


pytestmark = pytest.mark.asyncio


class TestNextRoundActionType:
    async def test_choice_at_basic_round_start(self, no_action):
        prev_action = no_action
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_buzz_after_basic_round_normal_tile_choice(
        self, single_round, choice, normal_tile
    ):
        prev_action = choice
        actual = await next_round_action_type(prev_action)
        expected = ActionType.BUZZ
        assert expected == actual

    async def test_wager_after_basic_round_daily_double_choice(
        self, single_round, choice, daily_double_tile
    ):
        prev_action = choice
        actual = await next_round_action_type(prev_action)
        expected = ActionType.WAGER
        assert expected == actual

    async def test_response_after_basic_round_buzz(
        self, single_round, buzz
    ):
        prev_action = buzz
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_response_after_basic_round_wager(
        self, single_round, wager
    ):
        prev_action = wager
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_choice_after_basic_round_wager_and_response(
        self, single_round, wager, response
    ):
        prev_action = response
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_choice_after_basic_round_correct_response(
        self, single_round, correct_response
    ):
        prev_action = correct_response
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_choice_after_basic_round_all_incorrect_responses(
        self, single_round, incorrect_response_1, incorrect_response_2
    ):
        prev_action = incorrect_response_2
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_buzz_after_basic_round_some_incorrect_responses(
        self, single_round, team_1, team_2, incorrect_response_1
    ):
        prev_action = incorrect_response_1
        actual = await next_round_action_type(prev_action)
        expected = ActionType.BUZZ
        assert expected == actual

    async def test_no_action_when_no_tiles_left_but_choice_would_be_next(
        self, single_round, choice_1, choice_2, response
    ):
        prev_action = response
        actual = await next_round_action_type(prev_action)
        expected = NoAction(single_round)
        assert expected == actual

    async def test_wager_at_final_round_start(
        self, final_round, no_action
    ):
        prev_action = no_action
        actual = await next_round_action_type(prev_action)
        expected = ActionType.WAGER
        assert expected == actual

    async def test_wager_after_final_round_some_wagers(
        self, final_round, team_1, team_2, wager_1
    ):
        prev_action = wager_1
        actual = await next_round_action_type(prev_action)
        expected = ActionType.WAGER
        assert expected == actual

    async def test_response_after_final_round_all_wagers(
        self, final_round, wager_1, wager_2
    ):
        prev_action = wager_2
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_response_after_final_round_some_responses(
        self, final_round, team_1, team_2, incorrect_response_1
    ):
        prev_action = incorrect_response_1
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_no_action_after_final_round_all_responses(
        self, final_round, incorrect_response_1, incorrect_response_2
    ):
        prev_action = incorrect_response_2
        actual = await next_round_action_type(prev_action)
        expected = NoAction(final_round)
        assert expected == actual


class TestPerform:
    async def test_next_message_id_increments(
        self, game_started_with_team_1, player_1, request_choice
    ):
        original_game = game_started_with_team_1
        expected = original_game.next_message_id + 1

        player = player_1
        action = request_choice.action
        await perform(original_game, player, action)

        updated_game = await GameOrm.get(id=original_game.id)
        actual = updated_game.next_message_id

        assert expected == actual

    async def test_next_round_changes_at_round_end(
        self,
        game_started_with_team_1,
        player_1,
        round_2,
        chosen_tile_1,
        request_response,
    ):
        original_game = game_started_with_team_1
        expected = round_2

        player = player_1
        action = request_response.action
        await perform(original_game, player, action)

        updated_game = await GameOrm.get(id=original_game.id)
        actual = await updated_game.next_round

        assert expected == actual

    @patch("jeopardy.play.next_round_action_type")
    async def test_checks_next_action_type(
        self,
        mock_next_round_action_type,
        game_started_with_team_1,
        player_1,
        request_buzz,
    ):
        mock_next_round_action_type.return_value=ActionType.CHOICE
        game = game_started_with_team_1
        player = player_1
        action = request_buzz.action
        await perform(game, player, action)

        mock_next_round_action_type.assert_called()

    async def test_next_action_type_changes_in_single_round(
        self, game_started_with_team_1, single_round, player_1, request_buzz
    ):
        player = player_1
        action = request_buzz.action

        # It's important to set original action type to match input request
        # type for this test to make sense
        original_game = game_started_with_team_1
        original_game.next_action_type = action.type_
        await original_game.save()
        original_next_action_type = original_game.next_action_type

        await perform(original_game, player, action)
        updated_game = await GameOrm.get(id=original_game.id)

        assert updated_game.next_action_type != original_next_action_type

    async def test_next_action_type_is_not_none_for_mid_game_round_changes(
        self,
        game_started_with_team_1,
        player_1,
        round_2,
        chosen_tile_1,
        request_response,
    ):
        player = player_1
        action = request_response.action

        original_game = game_started_with_team_1
        await perform(original_game, player, action)
        updated_game = await GameOrm.get(id=original_game.id)

        # Confirm round changed and is not null
        expected = round_2
        actual = await updated_game.next_round
        assert expected == actual
        assert await updated_game.next_round is not None

        # Confirm next action is not null
        assert updated_game.next_action_type is not None

    async def test_tile_count_of_action_type_increases(
        self, game_started_with_team_1, player_1, tile, request_wager
    ):
        original_tile = tile
        expected = len(await original_tile.wagers) + 1

        game = game_started_with_team_1
        player = player_1
        action = request_wager.action
        await perform(game, player, action)

        updated_tile = await TileOrm.get(id=tile.id)
        actual = len(await updated_tile.wagers)

        assert expected == actual

    async def test_next_chooser_changes_after_correct_response(
        self, game_started_with_team_1, player_2, tile_1, tile_2
    ):
        game = game_started_with_team_1
        correct_player = player_2
        correct_team = await correct_player.team(game)
        correct_response = Response(
            type="response",
            tile_id=tile_1.id,
            question=(await tile_1.trivia).question,
        )

        # Ensure original chooser is different from player providing correct
        # response
        assert await game.next_chooser != correct_team

        await perform(game, correct_player, correct_response)

        # Ensure updated chooser has changed
        expected = correct_team
        actual = await game.next_chooser
        assert expected == actual

    async def test_next_chooser_is_lowest_scorer_for_double_round_start(
        self, game_started_with_team_1, team_1, team_2, player_2, chosen_tile_1
    ):
        original_game = game_started_with_team_1
        original_round = await original_game.next_round
        correct_player = player_2
        correct_team = await correct_player.team(original_game)
        correct_response = Response(
            type="response",
            tile_id=chosen_tile_1.id,
            question=(await chosen_tile_1.trivia).question,
        )

        # Make team 1 the lower scoring team
        team_1.score = 100
        await team_1.save()
        team_2.score = 500
        await team_2.save()
        lowest_scoring_team = team_1

        # Ensure original chooser is different from player providing correct
        # response
        assert await original_game.next_chooser != correct_team

        await perform(original_game, correct_player, correct_response)

        # Ensure round has changed
        updated_game = await GameOrm.get(id=original_game.id)
        updated_round = await updated_game.next_round
        assert updated_round != original_round

        # Ensure updated chooser has changed to lowest scorer
        expected = lowest_scoring_team
        actual = await updated_game.next_chooser
        assert expected == actual

    async def test_score_increases_for_correct_normal_tile_response(
        self,
        game_started_with_team_1,
        single_round,
        team_1,
        player_1,
        normal_tile,
    ):
        original_score = team_1.score
        correct_response = Response(
            type="response",
            tile_id=normal_tile.id,
            question=(await normal_tile.trivia).question,
        )

        game = game_started_with_team_1
        player = player_1
        await perform(game, player, correct_response)

        expected = original_score + 200
        actual = (await TeamOrm.get(id=team_1.id)).score
        assert expected == actual

    async def test_score_decreases_for_incorrect_normal_tile_response(
        self,
        game_started_with_team_1,
        single_round,
        team_1,
        player_1,
        normal_tile,
    ):
        original_score = team_1.score
        incorrect_response = Response(
            type="response",
            tile_id=normal_tile.id,
            question="This is incorrect",
        )

        game = game_started_with_team_1
        player = player_1
        await perform(game, player, incorrect_response)

        expected = original_score - 200
        actual = (await TeamOrm.get(id=team_1.id)).score
        assert expected == actual

    async def test_score_changes_by_wager_amount_for_daily_double_response(
        self,
        game_started_with_team_1,
        single_round,
        team_1,
        player_1,
        daily_double_tile,
        wager,
    ):
        original_score = team_1.score
        correct_response = Response(
            type="response",
            tile_id=daily_double_tile.id,
            question=(await daily_double_tile.trivia).question,
        )

        game = game_started_with_team_1
        player = player_1
        await perform(game, player, correct_response)

        expected = original_score + wager.amount
        actual = (await TeamOrm.get(id=team_1.id)).score
        assert expected == actual

    async def test_score_changes_by_wager_amount_for_final_round(
        self,
        game_started_with_team_1,
        final_round,
        team_1,
        player_1,
        tile,
        wager,
    ):
        original_score = team_1.score
        incorrect_response = Response(
            type="response",
            tile_id=tile.id,
            question="This is incorrect",
        )

        game = game_started_with_team_1
        player = player_1
        await perform(game, player, incorrect_response)

        expected = original_score - wager.amount
        actual = (await TeamOrm.get(id=team_1.id)).score
        assert expected == actual
