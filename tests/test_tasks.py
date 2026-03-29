# tests/test_tasks.py

from app.models import Ticket
from app.tasks import get_expected_action


def test_expected_action_assign():
    ticket = Ticket(
        id=1,
        customer_name="User",
        issue="Unable to login",
        category="authentication"
    )

    expected = get_expected_action(ticket)
    assert expected["action_type"] == "assign"
    assert expected["team"] == "auth_team"