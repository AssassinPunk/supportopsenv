# scripts/baseline.py

from app.env import SupportOpsEnv
from app.models import Action


def rule_based_agent(ticket):
    if not ticket.category:
        return Action(
            action_type="classify",
            ticket_id=ticket.id,
            payload={"category": "general"}
        )

    if not ticket.assigned_to:
        team_map = {
            "billing": "billing_team",
            "authentication": "auth_team",
            "technical": "tech_team"
        }
        return Action(
            action_type="assign",
            ticket_id=ticket.id,
            payload={"team": team_map.get(ticket.category, "support_team")}
        )

    if not ticket.response_sent:
        return Action(
            action_type="respond",
            ticket_id=ticket.id,
            payload={"message": "We are working on your issue."}
        )

    return Action(
        action_type="resolve",
        ticket_id=ticket.id,
        payload={"resolution_note": "Issue resolved by baseline agent."}
    )


def main():
    env = SupportOpsEnv()
    result = env.reset()

    while not result.done:
        ticket = result.observation.ticket
        action = rule_based_agent(ticket)
        result = env.step(action)
        print(result.model_dump())

    print("Episode completed.")
    print(env.state().model_dump())


if __name__ == "__main__":
    main()