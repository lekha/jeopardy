from unittest.mock import patch

import pytest

from jeopardy.controllers.play import is_active_game
from jeopardy.controllers.play import is_permitted_to_act
from jeopardy.controllers.play import is_player
from jeopardy.controllers.play import is_valid_action
from jeopardy.controllers.play import next_round_action_type
from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass


pytestmark = pytest.mark.asyncio


class TestIsActiveGame:
    async def test_game_is_active_when_started_but_not_finished(self):
        game = GameOrm(is_started=True, is_finished=False)
        actual = await is_active_game(game)
        expected = True
        assert expected == actual

    async def test_game_is_inactive_when_not_started(self):
        game = GameOrm(is_started=False)
        actual = await is_active_game(game)
        expected = False
        assert expected == actual

    async def test_game_is_inactive_when_finished(self):
        game = GameOrm(is_finished=True)
        actual = await is_active_game(game)
        expected = False
        assert expected == actual


class TestIsPlayer:
    async def test_user_is_player_when_on_team(
        self, game, team, anonymous_user
    ):
        await team.players.add(anonymous_user)
        actual = await is_player(game, anonymous_user)
        expected = True
        assert expected == actual

    async def test_user_is_not_player_when_not_on_team(
        self, game, team, anonymous_user
    ):
        actual = await is_player(game, anonymous_user)
        expected = False
        assert expected == actual

    async def test_user_is_not_player_when_inactive(
        self, game, team, inactive_user
    ):
        await team.players.add(inactive_user)
        actual = await is_player(game, inactive_user)
        expected = False
        assert expected == actual


class TestIsPermittedToAct:
    async def test_permitted_only_if_choice_is_for_available_tile(
        self, game_with_team_1_next, single_round, player_1, tile, chosen_tile
    ):
        game = game_with_team_1_next
        action = ActionType.CHOICE

        expected = True
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = False
        actual = await is_permitted_to_act(game, player_1, action, chosen_tile)
        assert expected == actual

    async def test_permitted_only_if_choice_made_by_choosing_team(
        self, game_with_team_1_next, single_round, player_1, player_2, tile
    ):
        game = game_with_team_1_next
        action = ActionType.CHOICE

        expected = True
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = False
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual

    async def test_permitted_only_if_buzz_for_chosen_tile(
        self, game, single_round, player_1, tile, chosen_tile
    ):
        action = ActionType.BUZZ

        expected = False
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = True
        actual = await is_permitted_to_act(game, player_1, action, chosen_tile)
        assert expected == actual

    async def test_permitted_only_if_buzz_made_by_team_not_already_buzzed(
        self,
        game,
        single_round,
        player_1,
        player_2,
        tile,
        buzz_1_when_chosen_by_2,
    ):
        action = ActionType.BUZZ

        expected = False
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = True
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual

    async def test_permitted_only_if_response_made_by_team_that_buzzed(
        self,
        game,
        single_round,
        player_1,
        player_2,
        normal_tile,
        buzz_1_when_chosen_by_2,
    ):
        action = ActionType.RESPONSE
        tile = normal_tile

        expected = True
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = False
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual

    async def test_permitted_only_if_response_made_by_team_that_wagered(
        self,
        game,
        single_round,
        player_1,
        player_2,
        daily_double_tile,
        wager_1,
    ):
        action = ActionType.RESPONSE
        tile = daily_double_tile

        expected = True
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = False
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual

    async def test_permitted_only_if_wager_made_by_choosing_team(
        self,
        game,
        single_round,
        player_1,
        player_2,
        tile,
        choice_1,
    ):
        action = ActionType.WAGER

        expected = True
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = False
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual

    async def test_permitted_only_if_final_round_wager_not_already_made(
        self,
        game,
        final_round,
        player_1,
        player_2,
        tile,
        wager_1,
    ):
        action = ActionType.WAGER

        expected = False
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = True
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual

    async def test_permitted_only_if_final_round_response_not_already_made(
        self,
        game,
        final_round,
        player_1,
        player_2,
        tile,
        incorrect_response_1,
    ):
        action = ActionType.RESPONSE

        expected = False
        actual = await is_permitted_to_act(game, player_1, action, tile)
        assert expected == actual

        expected = True
        actual = await is_permitted_to_act(game, player_2, action, tile)
        assert expected == actual


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

    async def test_none_when_no_tiles_left_but_choice_would_be_next(
        self, single_round, choice_1, choice_2, response
    ):
        prev_action = response
        actual = await next_round_action_type(prev_action)
        expected = None
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

    async def test_none_after_final_round_all_responses(
        self, final_round, incorrect_response_1, incorrect_response_2
    ):
        prev_action = incorrect_response_2
        actual = await next_round_action_type(prev_action)
        expected = None
        assert expected == actual


class TestIsValidAction:
    async def test_valid_only_when_all_inputs_are_non_null(
        self, game_started_with_team_1, round_, team_1, player_1, tile
    ):
        action = ActionType.CHOICE
        game = game_started_with_team_1
        user = player_1

        expected = False
        actual = await is_valid_action(None, round_, user, action, tile)
        assert expected == actual

        expected = False
        actual = await is_valid_action(game, None, user, action, tile)
        assert expected == actual

        expected = False
        actual = await is_valid_action(game, round_, None, action, tile)
        assert expected == actual

        expected = False
        actual = await is_valid_action(game, round_, user, None, tile)
        assert expected == actual

        expected = False
        actual = await is_valid_action(game, round_, user, action, None)
        assert expected == actual

        expected = True
        actual = await is_valid_action(game, round_, user, action, tile)
        assert expected == actual

    @patch("jeopardy.controllers.play.is_active_game")
    async def test_valid_only_when_game_active(
        self, mock_is_active_game, game, round_, team_1, player_1, tile
    ):
        await is_valid_action(game, round_, player_1, ActionType.CHOICE, tile)
        mock_is_active_game.assert_called_with(game)

    async def test_valid_only_when_round_is_the_current_round(
        self, game_started_with_team_1, round_1, round_2, team_1, player_1, tile
    ):
        action = ActionType.CHOICE
        game = game_started_with_team_1
        user = player_1

        expected = True
        actual = await is_valid_action(game, round_1, user, action, tile)
        assert expected == actual

        expected = False
        actual = await is_valid_action(game, round_2, user, action, tile)
        assert expected == actual

    @patch("jeopardy.controllers.play.is_player")
    async def test_valid_only_when_user_is_a_player_in_the_game(
        self, mock_is_player, game, round_, team_1, player_1, tile
    ):
        await is_valid_action(game, round_, player_1, ActionType.CHOICE, tile)
        mock_is_player.assert_called_with(game, player_1)

    async def test_valid_only_when_action_is_the_next_allowed_type(
        self, game_started_with_team_1, round_, team_1, player_1, tile
    ):
        game = game_started_with_team_1

        action = ActionType.CHOICE
        expected = True
        actual = await is_valid_action(game, round_, player_1, action, tile)
        assert expected == actual

        action = ActionType.BUZZ
        expected = False
        actual = await is_valid_action(game, round_, player_1, action, tile)
        assert expected == actual

    @patch("jeopardy.controllers.play.is_permitted_to_act")
    async def test_valid_only_when_user_is_permitted_to_perform_the_action(
        self,
        mock_is_permitted_to_act,
        game_started_with_team_1,
        round_,
        team_1,
        player_1,
        tile,
    ):
        action = ActionType.CHOICE
        game = game_started_with_team_1

        await is_valid_action(game, round_, player_1, action, tile)
        mock_is_permitted_to_act.assert_called_with(
            game, player_1, action, tile
        )
