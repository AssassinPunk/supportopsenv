# app/policies.py

from typing import Tuple
from .models import Ticket, Action


def validate_action(ticket: Ticket, action: Action) -> Tuple[bool, str]:
    """
    Checks whether an action is allowed on the ticket.
    """

    if ticket.id != action.ticket_id:
        return False, "Ticket ID mismatch."

    if ticket.status in ["resolved", "closed"] and action.action_type != "resolve":
        return False, "No further action allowed on resolved/closed ticket."

    if action.action_type == "assign":
        if "team" not in action.payload:
            return False, "Assign action requires 'team' in payload."

    if action.action_type == "respond":
        if "message" not in action.payload:
            return False, "Respond action requires 'message' in payload."

    if action.action_type == "classify":
        if "category" not in action.payload:
            return False, "Classify action requires 'category' in payload."

    if action.action_type == "resolve":
        if "resolution_note" not in action.payload:
            return False, "Resolve action requires 'resolution_note' in payload."

    return True, "Valid action."