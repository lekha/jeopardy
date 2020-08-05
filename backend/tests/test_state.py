import pytest

import jeopardy.state as state


pytestmark = pytest.mark.asyncio


class TestFull:
    async def test_state_exists_for_game_with_teams_and_tiles(
        self,
        game_started_with_team_1,
        player_1,
        player_2,
        round_,
        tile,
        tile_2,
    ):
        game = game_started_with_team_1
        await state.current(game.code)
