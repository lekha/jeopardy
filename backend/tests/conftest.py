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

from jeopardy.models.game import GameOrm
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
async def team(database_schema, game):
    _team = TeamOrm(game=game, name="Test Team")
    await _team.save()
    yield _team
