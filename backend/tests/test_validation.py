from unittest.mock import patch

import pytest

from jeopardy.validation import is_active_game
from jeopardy.validation import is_permitted_to_act
from jeopardy.validation import is_player
from jeopardy.validation import is_valid_action
from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm


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

    @patch("jeopardy.validation.is_active_game")
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

    @patch("jeopardy.validation.is_player")
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

    @patch("jeopardy.validation.is_permitted_to_act")
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
