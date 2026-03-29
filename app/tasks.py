from typing import Dict, Any
from .models import Ticket


def get_expected_action(ticket: Ticket) -> Dict[str, Any]:
    """
    Defines the expected next action for a ticket.
    """

    if ticket.status in ["resolved", "closed"]:
        return {"action_type": "resolve"}

    if not ticket.category:
        return {"action_type": "classify"}

    if not ticket.assigned_to:
        team_map = {
            "billing": "billing_team",
            "authentication": "auth_team",
            "technical": "tech_team",
        }
        return {
            "action_type": "assign",
            "team": team_map.get(ticket.category, "support_team")
        }

    if not ticket.response_sent:
        return {"action_type": "respond"}

    return {"action_type": "resolve"}