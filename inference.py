from dotenv import load_dotenv
from openai import OpenAI
import os

from app.env import SupportOpsEnv
from app.models import Action

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = os.getenv("MODEL_NAME")

print("API_BASE_URL:", API_BASE_URL)
print("MODEL:", MODEL)
print("HF_TOKEN loaded:", bool(HF_TOKEN))
print("HF_TOKEN preview:", (HF_TOKEN or "")[:10])

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)


def build_prompt(ticket):
    return f"""
You are helping with a customer support workflow.

Ticket details:
- Issue: {ticket.issue}
- Category: {ticket.category}
- Priority: {ticket.priority}
- Assigned To: {ticket.assigned_to}
- Response Sent: {ticket.response_sent}
- Status: {ticket.status}

Workflow rule:
1. If not assigned -> assign to correct team
2. If assigned but not responded -> respond
3. If responded -> resolve

Return only one short text snippet useful for the next step.
Do not return action names.
""".strip()


def choose_action(ticket) -> Action:
    team_map = {
        "billing": "billing_team",
        "authentication": "auth_team",
        "technical": "tech_team",
    }

    if not ticket.assigned_to:
        return Action(
            action_type="assign",
            ticket_id=ticket.id,
            payload={"team": team_map.get(ticket.category, "support_team")}
        )

    if not ticket.response_sent:
        return Action(
            action_type="respond",
            ticket_id=ticket.id,
            payload={"message": "We are working on your issue and will update you shortly."}
        )

    return Action(
        action_type="resolve",
        ticket_id=ticket.id,
        payload={"resolution_note": "Issue resolved successfully."}
    )


def main():
    if not API_BASE_URL or not HF_TOKEN or not MODEL:
        print("Missing environment variables. Check your .env file.")
        return

    env = SupportOpsEnv()
    result = env.reset()

    print("\nRunning inference...\n")

    while not result.done:
        ticket = result.observation.ticket
        print("Current ticket state:", ticket.model_dump())

        prompt = build_prompt(ticket)

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise support assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                temperature=0.2,
                max_tokens=60,
            )

            output = response.choices[0].message.content or ""
            print("Model helper text:", output)

        except Exception as e:
            print(f"API call failed: {e}")
            output = ""

        action = choose_action(ticket)
        print(f"Chosen Action: {action.model_dump()}")

        result = env.step(action)

        print(f"Reward: {result.reward}")
        print(f"Done: {result.done}")
        print("-" * 50)

    print("Finished.")
    print(env.state().model_dump())


if __name__ == "__main__":
    main()