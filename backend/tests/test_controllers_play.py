import pytest

from jeopardy.controllers.play import is_active_game
from jeopardy.controllers.play import is_player
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
