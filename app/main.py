# app/main.py

from app.env import SupportOpsEnv
from app.models import Action


def run_demo():
    env = SupportOpsEnv()
    result = env.reset()

    print("RESET")
    print(result.model_dump())
    print("-" * 50)

    actions = [
        Action(action_type="assign", ticket_id=1, payload={"team": "billing_team"}),
        Action(action_type="respond", ticket_id=1, payload={"message": "We are checking your payment issue."}),
        Action(action_type="resolve", ticket_id=1, payload={"resolution_note": "Payment reconciled and confirmed."}),

        Action(action_type="assign", ticket_id=2, payload={"team": "auth_team"}),
        Action(action_type="respond", ticket_id=2, payload={"message": "Please try password reset once."}),
        Action(action_type="resolve", ticket_id=2, payload={"resolution_note": "User login restored successfully."}),

        Action(action_type="assign", ticket_id=3, payload={"team": "billing_team"}),
        Action(action_type="respond", ticket_id=3, payload={"message": "Invoice has been generated."}),
        Action(action_type="resolve", ticket_id=3, payload={"resolution_note": "Invoice sent to customer email."}),

        Action(action_type="assign", ticket_id=4, payload={"team": "tech_team"}),
        Action(action_type="respond", ticket_id=4, payload={"message": "We are investigating the crash issue."}),
        Action(action_type="resolve", ticket_id=4, payload={"resolution_note": "Bug fixed and patch released."}),
    ]

    for action in actions:
        result = env.step(action)
        print("STEP RESULT")
        print(result.model_dump())
        print("-" * 50)

        if result.done:
            break

    print("FINAL STATE")
    print(env.state().model_dump())


if __name__ == "__main__":
    run_demo()