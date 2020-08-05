from fastapi import HTTPException
from fastapi import status
from fastapi.security import SecurityScopes

from jeopardy.models.action import ActionType


def _auth_header(required: SecurityScopes, error_code: str = None) -> str:
    if required is not None:
        auth_header = f'Bearer scope="{required.scope_str}"'
    else:
        auth_header = f'Bearer realm="api"'

    if error_code:
        auth_header += f', error_code="{error_code}"'

    return auth_header


class UnauthorizedException(HTTPException):
    """HTTP Exception for 401 status codes."""
    def __init__(
        self, required: SecurityScopes, error_code: str, detail: str
    ) -> None:
        super().__init__(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = detail, 
            headers = {"WWW-Authenticate": _auth_header(required, error_code)},
        )

class InsufficientScopeException(UnauthorizedException):
    """HTTP Exception that follows IANA RFC 6750 standard.

    Link to standard:
        https://tools.ietf.org/html/rfc6750#section-3
    """
    def __init__(self, required: SecurityScopes) -> None:
        detail = "Not enough permissions"
        super().__init__(required, "insufficient_scope", detail)


class InvalidTokenException(UnauthorizedException):
    def __init__(self, required: SecurityScopes) -> None:
        detail = "Provided credentials are not valid"
        super().__init__(required, "invalid_token", detail)


class MissingTokenException(UnauthorizedException):
    def __init__(self, required: SecurityScopes) -> None:
        detail = "No credentials provided"
        super().__init__(required, None, detail)


class ForbiddenAccessException(Exception):
    """Exception when user attempts to access a game without permission."""
    pass


class TeamAtMaxCapacityException(ForbiddenAccessException):
    """Exception when the team cannot accept any additional players."""
    pass


class InvalidRequestException(Exception):
    """Exception for invalid incoming requests from users."""
    pass


class ActOutOfTurnException(InvalidRequestException):
    """Exception when user requests to perform action when not her turn."""
    pass


class ForbiddenActionException(InvalidRequestException):
    """Exception when user requests to perform inappropriate action."""
    def __init__(self, expected_action: ActionType) -> None:
        message = f"Forbidden action. Expected action type: {expected_action}"
        super().__init__(message)


class ForbiddenWagerException(InvalidRequestException):
    """Exception when player wagers a forbidden amount."""
    pass


class MissingFieldException(InvalidRequestException):
    """Exception when request is missing required fields."""
    def __init__(self, expected_schema: dict) -> None:
        message = f"Field missing. Expected request schema: {expected_schema}"
        super().__init__(message)


class TileAlreadyChosenException(InvalidRequestException):
    """Exception when player chooses a tile that has already been chosen."""
    pass


class TileNotFoundException(InvalidRequestException):
    """Exception when player chooses a tile that isn't part of the game."""
    pass
