# tests/test_grader.py

from app.models import Ticket, Action
from app.grader import grade_action


def test_grade_correct_assign():
    ticket = Ticket(
        id=1,
        customer_name="Test",
        issue="Payment failed",
        category="billing"
    )

    action = Action(
        action_type="assign",
        ticket_id=1,
        payload={"team": "billing_team"}
    )

    assert grade_action(ticket, action) == 1.0