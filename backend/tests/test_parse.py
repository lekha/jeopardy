import pytest

from jeopardy.exceptions import ForbiddenActionException
from jeopardy.exceptions import InvalidRequestException
from jeopardy.exceptions import MissingFieldException
from jeopardy.models.action import ActionType
from jeopardy.models.game import TileOrm
from jeopardy.parse import parse_request
from jeopardy.schema.action import Action
from jeopardy.schema.action import Response
from jeopardy.schema.action import Wager
from jeopardy.schema.action import Request


pytestmark = pytest.mark.asyncio


@pytest.fixture(params=["buzz", "choice", "response", "wager"])
def incoming_request(
    request,
    incoming_request_buzz,
    incoming_request_choice,
    incoming_request_response,
    incoming_request_wager,
):
    param_to_fixture = {
        "buzz":     (ActionType.BUZZ,     incoming_request_buzz),
        "choice":   (ActionType.CHOICE,   incoming_request_choice),
        "response": (ActionType.RESPONSE, incoming_request_response),
        "wager":    (ActionType.WAGER,    incoming_request_wager),
    }
    return param_to_fixture[request.param]


class TestParseRequest:
    def test_output_is_request_type(self, incoming_request):
        request = parse_request(*incoming_request)
        assert isinstance(request, Request)

    def test_output_action_type_is_enum_instead_of_string(
        self, incoming_request
    ):
        request = parse_request(*incoming_request)
        assert isinstance(request.action.type_, ActionType)

    def test_output_action_is_action_type_for_buzz(
        self, incoming_request_buzz
    ):
        type_ = ActionType.BUZZ
        request = parse_request(type_, incoming_request_buzz)
        assert isinstance(request.action, Action)

    def test_output_action_is_action_type_for_choice(
        self, incoming_request_choice
    ):
        type_ = ActionType.CHOICE
        request = parse_request(type_, incoming_request_choice)
        assert isinstance(request.action, Action)

    def test_output_action_is_response_type_for_response(
        self, incoming_request_response
    ):
        type_ = ActionType.RESPONSE
        request = parse_request(type_, incoming_request_response)
        assert isinstance(request.action, Response)

    def test_output_action_is_wager_type_for_wager(
        self, incoming_request_wager
    ):
        type_ = ActionType.WAGER
        request = parse_request(type_, incoming_request_wager)
        assert isinstance(request.action, Wager)

    def test_errors_when_invalid_action_type(self):
        type_ = ActionType.BUZZ
        inconsistent_request = {
            "message_id": 4,  # random
            "action": {
                "type": "invalid_action",
                "tile_id": 4,  # random
            },
        }
        with pytest.raises(ForbiddenActionException):
            parse_request(type_, inconsistent_request)

    def test_errors_when_input_request_does_not_match_action_type(
        self, incoming_request_response
    ):
        type_ = ActionType.BUZZ
        with pytest.raises(ForbiddenActionException):
            parse_request(type_, incoming_request_response)

    def test_does_not_error_when_extra_fields(self):
        type_ = ActionType.BUZZ
        request_with_extra_fields = {
            "message_id": 2,  # random
            "action": {
                "type": "buzz",
                "tile_id": 6,  # random
                "extra_field": "test",
            },
            "another_extra_field": "test",
        }

        parse_request(type_, request_with_extra_fields)

    def test_errors_when_missing_fields(self):
        type_ = ActionType.CHOICE
        request_with_missing_fields = {
            "action": {
                "type": "choice",
                "tile_id": 3,  # random
            },
        }
        with pytest.raises(MissingFieldException):
            parse_request(type_, request_with_missing_fields)
