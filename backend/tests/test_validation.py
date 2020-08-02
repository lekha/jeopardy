from unittest.mock import patch

import pytest

from jeopardy import exceptions
from jeopardy.models.action import ActionType
from jeopardy.models.game import GameOrm
from jeopardy.schema.action import Action
from jeopardy.schema.action import Request
from jeopardy.schema.action import Wager
from jeopardy.validation import is_active_game
from jeopardy.validation import is_permitted_to_act
from jeopardy.validation import is_permitted_wager
from jeopardy.validation import is_player
from jeopardy.validation import validate_game
from jeopardy.validation import validate_request
from jeopardy.validation import validate_user


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


class TestIsPermittedWager:
    async def test_permitted_for_valid_wagers(self, team_1):
        team_1.score = 400
        await team_1.save()

        valid_amount = 300
        expected = True
        actual = is_permitted_wager(team_1, valid_amount)
        assert expected == actual

    @pytest.mark.parametrize("amount", [14, 69, 88, 666, 1488])
    async def test_errors_for_amounts_prohibited_(self, team_1, amount):
        team_1.score = 3000
        await team_1.save()

        expected = False
        actual = is_permitted_wager(team_1, amount)
        assert expected == actual

    async def test_errors_for_amounts_above_team_score(self, team_1):
        team_1.score = 200
        await team_1.save()

        too_large_amount = 300
        expected = False
        actual = is_permitted_wager(team_1, too_large_amount)
        assert expected == actual

    async def test_errors_for_negative_amounts(self, team_1):
        too_low_amount = -5
        expected = False
        actual = is_permitted_wager(team_1, too_low_amount)
        assert expected == actual


class TestValidateGame:
    async def test_errors_if_game_does_not_exist(self):
        game = None
        with pytest.raises(exceptions.ForbiddenAccessException):
            await validate_game(game)

    async def test_errors_if_game_is_not_active(self):
        game = GameOrm(is_started=True, is_finished=True)
        with pytest.raises(exceptions.ForbiddenAccessException):
            await validate_game(game)

    @patch("jeopardy.validation.is_active_game")
    async def test_checks_if_game_is_active(self, mock_is_active_game):
        game = GameOrm(is_started=True, is_finished=True)
        await validate_game(game)
        mock_is_active_game.assert_called_with(game)


class TestValidateRequest:
    async def test_does_not_error_for_logically_consistent_input(
        self, game_started_with_team_1, player_1, tile
    ):
        game = game_started_with_team_1
        user = player_1
        consistent_request = Request(
            message_id=game.next_message_id,
            action=Action(type="choice", tile_id=tile.id),
        )

        await validate_request(game, user, consistent_request)

    async def test_errors_when_message_id_not_next(
        self, game_started_with_team_1, player_1, tile
    ):
        game = game_started_with_team_1
        user = player_1
        inconsistent_request = Request(
            message_id=game.next_message_id - 1,
            action=Action(type="choice", tile_id=tile.id),
        )

        with pytest.raises(exceptions.InvalidRequestException):
            await validate_request(game, user, inconsistent_request)

    async def test_errors_when_action_type_not_next(
        self, game_started_with_team_1, player_1, tile
    ):
        game = game_started_with_team_1
        user = player_1
        forbidden_request = Request(
            message_id=game.next_message_id,
            action=Action(type="buzz", tile_id=tile.id),
        )

        with pytest.raises(exceptions.ForbiddenActionException):
            await validate_request(game, user, forbidden_request)

    async def test_errors_when_tile_not_found(
        self, game_started_with_team_1, player_1, tile
    ):
        game = game_started_with_team_1
        user = player_1
        inconsistent_request = Request(
            message_id=game.next_message_id,
            action=Action(type="choice", tile_id=tile.id + 1),
        )

        with pytest.raises(exceptions.TileNotFoundException):
            await validate_request(game, user, inconsistent_request)

    async def test_errors_when_tile_not_part_of_game(
        self, game_started_with_team_1, player_1, round_2_tile
    ):
        game = game_started_with_team_1
        user = player_1
        inconsistent_request = Request(
            message_id=game.next_message_id,
            action=Action(type="choice", tile_id=round_2_tile.id),
        )

        with pytest.raises(exceptions.TileNotFoundException):
            await validate_request(game, user, inconsistent_request)

    async def test_errors_when_tile_already_chosen(
        self, game_started_with_team_1, player_1, chosen_tile
    ):
        game = game_started_with_team_1
        user = player_1
        forbidden_request = Request(
            message_id=game.next_message_id,
            action=Action(type="choice", tile_id=chosen_tile.id),
        )

        with pytest.raises(exceptions.TileAlreadyChosenException):
            await validate_request(game, user, forbidden_request)

    async def test_errors_when_wager_amount_is_explicitly_prohibited(
        self, game_after_daily_double_chosen, player_1, tile
    ):
        game = game_after_daily_double_chosen
        user = player_1
        forbidden_request = Request(
            message_id=game.next_message_id,
            action=Wager(type="wager", tile_id=tile.id, amount=666),
        )

        with pytest.raises(exceptions.ForbiddenWagerException):
            await validate_request(game, user, forbidden_request)

    @patch("jeopardy.validation.is_permitted_wager")
    async def test_checks_when_wager_is_permitted(
        self,
        mock_is_permitted_wager,
        game_after_daily_double_chosen,
        team_1,
        player_1,
        tile,
    ):
        valid_amount = 100
        team_1.score = 150
        await team_1.save()

        game = game_after_daily_double_chosen
        user = player_1
        request = Request(
            message_id=game.next_message_id,
            action=Wager(type="wager", tile_id=tile.id, amount=valid_amount)
        )

        await validate_request(game, user, request)
        mock_is_permitted_wager.assert_called_with(team_1, valid_amount)

    async def test_errors_if_user_not_permitted_to_perform_the_action(
        self, game_started_with_team_1, player_2, tile
    ):
        game = game_started_with_team_1
        wrong_user = player_2
        consistent_request = Request(
            message_id=game.next_message_id,
            action=Action(type="choice", tile_id=tile.id),
        )

        with pytest.raises(exceptions.ActOutOfTurnException):
            await validate_request(game, wrong_user, consistent_request)


class TestValidateUser:
    async def test_errors_if_user_not_player(self, game, anonymous_user):
        with pytest.raises(exceptions.ForbiddenAccessException):
            await validate_user(game, anonymous_user)

    @patch("jeopardy.validation.is_player")
    async def test_checks_if_user_is_player(
        self, mock_is_player, game, player_1
    ):
        await validate_user(game, player_1)
        mock_is_player.assert_called_with(game, player_1)
