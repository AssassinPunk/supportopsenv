from .models import Ticket, Action
from .tasks import get_expected_action


def grade_action(ticket: Ticket, action: Action) -> float:
    """
    Returns a score for how correct the action is.
    """

    expected = get_expected_action(ticket)

    if action.action_type != expected["action_type"]:
        return -1.0

    if action.action_type == "assign":
        team = action.payload.get("team")
        return 1.0 if team == expected.get("team") else 0.0

    return 1.0