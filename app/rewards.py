from .models import Ticket, Action
from .grader import grade_action


def compute_reward(ticket: Ticket, action: Action) -> float:
    base_score = grade_action(ticket, action)

    if base_score < 0:
        return base_score

    if action.action_type == "resolve" and ticket.priority in ["high", "urgent"]:
        base_score += 0.5

    return base_score