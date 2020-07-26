import pytest

from jeopardy.play import next_round_action_type
from jeopardy.models.action import ActionType


pytestmark = pytest.mark.asyncio


class TestNextRoundActionType:
    async def test_choice_at_basic_round_start(self, no_action):
        prev_action = no_action
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_buzz_after_basic_round_normal_tile_choice(
        self, single_round, choice, normal_tile
    ):
        prev_action = choice
        actual = await next_round_action_type(prev_action)
        expected = ActionType.BUZZ
        assert expected == actual

    async def test_wager_after_basic_round_daily_double_choice(
        self, single_round, choice, daily_double_tile
    ):
        prev_action = choice
        actual = await next_round_action_type(prev_action)
        expected = ActionType.WAGER
        assert expected == actual

    async def test_response_after_basic_round_buzz(
        self, single_round, buzz
    ):
        prev_action = buzz
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_response_after_basic_round_wager(
        self, single_round, wager
    ):
        prev_action = wager
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_choice_after_basic_round_wager_and_response(
        self, single_round, wager, response
    ):
        prev_action = response
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_choice_after_basic_round_correct_response(
        self, single_round, correct_response
    ):
        prev_action = correct_response
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_choice_after_basic_round_all_incorrect_responses(
        self, single_round, incorrect_response_1, incorrect_response_2
    ):
        prev_action = incorrect_response_2
        actual = await next_round_action_type(prev_action)
        expected = ActionType.CHOICE
        assert expected == actual

    async def test_buzz_after_basic_round_some_incorrect_responses(
        self, single_round, team_1, team_2, incorrect_response_1
    ):
        prev_action = incorrect_response_1
        actual = await next_round_action_type(prev_action)
        expected = ActionType.BUZZ
        assert expected == actual

    async def test_none_when_no_tiles_left_but_choice_would_be_next(
        self, single_round, choice_1, choice_2, response
    ):
        prev_action = response
        actual = await next_round_action_type(prev_action)
        expected = None
        assert expected == actual

    async def test_wager_at_final_round_start(
        self, final_round, no_action
    ):
        prev_action = no_action
        actual = await next_round_action_type(prev_action)
        expected = ActionType.WAGER
        assert expected == actual

    async def test_wager_after_final_round_some_wagers(
        self, final_round, team_1, team_2, wager_1
    ):
        prev_action = wager_1
        actual = await next_round_action_type(prev_action)
        expected = ActionType.WAGER
        assert expected == actual

    async def test_response_after_final_round_all_wagers(
        self, final_round, wager_1, wager_2
    ):
        prev_action = wager_2
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_response_after_final_round_some_responses(
        self, final_round, team_1, team_2, incorrect_response_1
    ):
        prev_action = incorrect_response_1
        actual = await next_round_action_type(prev_action)
        expected = ActionType.RESPONSE
        assert expected == actual

    async def test_none_after_final_round_all_responses(
        self, final_round, incorrect_response_1, incorrect_response_2
    ):
        prev_action = incorrect_response_2
        actual = await next_round_action_type(prev_action)
        expected = None
        assert expected == actual
