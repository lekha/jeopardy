from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send


class AuthenticationMiddleware:
    """Simplify browser API calls by moving the user cookie to a header.

    Using the cookie in the browser is convenient because it enables easy login
    and logout across all tabs in a browser as well as simplifies automatic
    logout when the browser is closed.

    Using the Authorization header for API calls to the backend is convenient
    because it enables cleaner generated docs and simplifies non-browser API
    calls (e.g. testing). It's also considered a best practice generally.

    Thus, this is the interface that allows the browser to continue using
    cookies while the backend only accepts API calls with auth information in
    the header.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            connection = HTTPConnection(scope)
            if "user" in connection.cookies:
                user_auth = connection.cookies["user"]
                headers = MutableHeaders(scope=scope)
                headers.setdefault("Authorization", user_auth)
        await self.app(scope, receive, send)
