from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.schema.state import Game


async def current(game_code: str) -> Game:
    """Fetch the full current state of the game."""
    # Fetch needed values from database
    game_orm = await GameOrm.get(code=game_code)
    await game_orm.fetch_related("teams__players")
    await game_orm.fetch_related("next_round__board__categories__tiles__trivia")
    await game_orm.fetch_related("next_chooser")

    # Transform database orm to pydantic model
    state = Game.from_orm(game_orm)

    # Set points for tiles in basic rounds
    if state.round_.class_ != RoundClass.FINAL:
        if state.round_.class_ == RoundClass.SINGLE:
            multiplier = 200
        else:
            multiplier = 400
        for category in state.round_.board.categories:
            for position, tile in enumerate(category.tiles):
                tile.points = multiplier * (position + 1)

    return state
