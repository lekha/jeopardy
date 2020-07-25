from os import getenv

import asyncio
import pytest
from pymysql.constants import CLIENT
from tortoise import Tortoise
from yoyo import get_backend
from yoyo import read_migrations
from yoyo.backends import MySQLBackend
from yoyo.connections import parse_uri
from yoyo.migrations import default_migration_table

from jeopardy.models.action import BuzzOrm
from jeopardy.models.action import ChoiceOrm
from jeopardy.models.action import NoAction
from jeopardy.models.action import ResponseOrm
from jeopardy.models.action import WagerOrm
from jeopardy.models.game import BoardOrm
from jeopardy.models.game import CategoryOrm
from jeopardy.models.game import GameOrm
from jeopardy.models.game import RoundClass
from jeopardy.models.game import RoundOrm
from jeopardy.models.game import TileOrm
from jeopardy.models.game import TriviaOrm
from jeopardy.models.team import TeamOrm
from jeopardy.models.user import UserOrm


def _get_backend(uri, migration_table=default_migration_table):
    """Patch of yoyo's original get_backend() function.

    Original implementation is here:
    https://hg.sr.ht/~olly/yoyo/browse/yoyo/connections.py?rev=387b00ee5596b63cb93bf79fa3d4112576679bc0#L82

    Patching is needed for the same reason documented elsewhere in this
    codebase:
    https://github.com/lekha/jeopardy/commit/76e8b7ebd8abb0e2ad6ff7547ad74ae7b60d1690
    """
    if uri.startswith("mysql://"):
        parsed_uri = parse_uri(uri)
        parsed_uri.args["client_flag"] = CLIENT.MULTI_STATEMENTS
        backend = MySQLBackend(parsed_uri, migration_table)
    else:
        backend = get_backend(uri, migration_table)

    return backend


@pytest.yield_fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def database():
    database_uri = getenv("DATABASE_URI")
    await Tortoise.init(
        db_url=database_uri,
        modules={"models": ["jeopardy.models"]},
    )


@pytest.fixture
def database_schema(database):
    migrations_dir = getenv("MIGRATIONS_DIR")
    migrations = read_migrations(migrations_dir)

    database_uri = getenv("DATABASE_URI")
    backend = _get_backend(database_uri)

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

    yield

    with backend.lock():
        backend.rollback_migrations(backend.to_rollback(migrations))


@pytest.fixture
async def google_user(database_schema):
    user = UserOrm(
        username="test_google_user",
        is_active=True,
        auth_provider="google",
    )
    await user.save()
    yield user


@pytest.fixture
async def inactive_user(database_schema):
    user = UserOrm(
        username="test_inactive_user",
        is_active=False,
        auth_provider="google",
    )
    await user.save()
    yield user


@pytest.fixture
async def anonymous_user(database_schema):
    user = UserOrm(
        username="test_anonymous_user",
        is_active=True,
        auth_provider="none",
    )
    await user.save()
    yield user


@pytest.fixture
async def game(database_schema, google_user):
    _game = GameOrm(
        name="Test Game",
        code="TEST",
        owner=google_user,
        max_teams=3,
        max_players_per_team=3,
        is_started=True,
        is_finished=False,
    )
    await _game.save()
    yield _game


@pytest.fixture
async def round(database_schema, game):
    _round = RoundOrm(game=game, class_=RoundClass.SINGLE, ordinal=1)
    await _round.save()
    yield _round


@pytest.fixture
async def single_round(database_schema, round):
    yield round


@pytest.fixture
async def final_round(database_schema, round):
    round.class_ = RoundClass.FINAL
    round.ordinal = 3
    await round.save()
    yield round


@pytest.fixture
async def tile(database, round):
    board = BoardOrm(
        round=round,
        num_categories=2,
        num_tiles_per_category=2,
    )
    await board.save()

    category = CategoryOrm(
        board=board,
        name="Test Category",
        ordinal=0,
    )
    await category.save()

    trivia = TriviaOrm(
        answer="Test answer",
        question="Test question?",
    )
    await trivia.save()

    _tile = TileOrm(
        category=category,
        trivia=trivia,
        ordinal=0,
    )
    await _tile.save()
    yield _tile


@pytest.fixture
async def normal_tile(database_schema, tile):
    yield tile


@pytest.fixture
async def daily_double_tile(database_schema, tile):
    tile.is_daily_double = True
    await tile.save()
    yield tile


@pytest.fixture
async def tile_1(database_schema, tile):
    yield tile


@pytest.fixture
async def tile_2(database_schema, tile):
    trivia = TriviaOrm(
        answer="Test answer 2",
        question="Test question 2?",
    )
    await trivia.save()

    _tile = tile.clone()
    _tile.ordinal += 1
    _tile.trivia = trivia
    await _tile.save()
    yield _tile


@pytest.fixture
async def chosen_tile(database_schema, game, team_2, player_2, tile_2):
    await ChoiceOrm.create(
        game=game, tile=tile_2, team=team_2, user=player_2
    )
    yield tile_2


@pytest.fixture
async def team(database_schema, game):
    _team = TeamOrm(game=game, name="Test Team")
    await _team.save()
    yield _team


@pytest.fixture
async def team_1(database_schema, game):
    _team = TeamOrm(game=game, name="Test Team 1")
    await _team.save()
    yield _team


@pytest.fixture
async def team_2(database_schema, game):
    _team = TeamOrm(game=game, name="Test Team 2")
    await _team.save()
    yield _team


@pytest.fixture
async def player_1(database_schema, anonymous_user, team_1):
    player = anonymous_user.clone()
    player.username = "player_1"
    await player.save()
    await team_1.players.add(player)
    yield player


@pytest.fixture
async def player_2(database_schema, anonymous_user, team_2):
    player = anonymous_user.clone()
    player.username = "player_2"
    await player.save()
    await team_2.players.add(player)
    yield player


@pytest.fixture
def no_action(round):
    return NoAction(round)


@pytest.fixture
async def buzz(database_schema, game, tile, team_1, player_1):
    _buzz = BuzzOrm(game=game, tile=tile, team=team_1, user=player_1)
    await _buzz.save()
    yield _buzz


@pytest.fixture
async def buzz_1_when_chosen_by_2(database_schema, choice_2, buzz):
    yield buzz


@pytest.fixture
async def choice(database_schema, game, tile, team_1, player_1):
    _choice = ChoiceOrm(game=game, tile=tile, team=team_1, user=player_1)
    await _choice.save()
    yield _choice


@pytest.fixture
async def choice_1(database_schema, choice):
    yield choice


@pytest.fixture
async def choice_2(database_schema, choice, tile_2):
    _choice = choice.clone()
    _choice.tile = tile_2
    await _choice.save()
    yield _choice


@pytest.fixture
async def response(database_schema, game, tile, team_1, player_1):
    _response = ResponseOrm(game=game, tile=tile, team=team_1, user=player_1)
    _response.is_correct = False
    await _response.save()
    yield _response


@pytest.fixture
async def correct_response(database_schema, response):
    response.is_correct = True
    await response.save()
    yield response


@pytest.fixture
async def incorrect_response_1(database_schema, response):
    yield response


@pytest.fixture
async def incorrect_response_2(database_schema, response, team_2, player_2):
    _response = response.clone()
    _response.team = team_2
    _response.user = player_2
    await _response.save()
    yield _response


@pytest.fixture
async def wager(database_schema, game, tile, team_1, player_1):
    _wager = WagerOrm(game=game, tile=tile, team=team_1, user=player_1)
    _wager.amount = 100
    await _wager.save()
    yield _wager


@pytest.fixture
async def wager_1(database_schema, wager):
    yield wager


@pytest.fixture
async def wager_2(database_schema, wager, team_2, player_2):
    _wager = wager.clone()
    _wager.team = team_2
    _wager.user = player_2
    await _wager.save()
    yield _wager


@pytest.fixture
async def game_with_team_1_next(database_schema, game, team_1):
    game.next_chooser = team_1
    await game.save()
    yield game
