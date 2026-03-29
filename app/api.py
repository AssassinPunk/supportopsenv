from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

from app.env import SupportOpsEnv
from app.models import Action

app = FastAPI(title="SupportOpsEnv API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SupportOpsEnv()
env.reset()

reward_history: List[float] = []


class ActionRequest(BaseModel):
    action_type: str
    ticket_id: int
    payload: Dict[str, Any] = {}


def choose_best_action(ticket) -> Action:
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


@app.get("/")
def root():
    return {"message": "SupportOpsEnv API is running"}


@app.post("/reset")
def reset_env():
    global reward_history
    reward_history = []
    result = env.reset()
    return result.model_dump()


@app.get("/state")
def get_state():
    return env.state().model_dump()


@app.get("/current-ticket")
def get_current_ticket():
    if env.done or env.current_index >= len(env.tickets):
        return {"ticket": None, "done": True}
    return {
        "ticket": env.tickets[env.current_index].model_dump(),
        "done": env.done,
    }


@app.post("/step")
def step_env(action_req: ActionRequest):
    try:
        action = Action(
            action_type=action_req.action_type,
            ticket_id=action_req.ticket_id,
            payload=action_req.payload,
        )
        result = env.step(action)
        reward_history.append(result.reward)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auto-step")
def auto_step():
    if env.done or env.current_index >= len(env.tickets):
        return {"message": "All tickets already completed.", "done": True}

    ticket = env.tickets[env.current_index]
    action = choose_best_action(ticket)
    result = env.step(action)
    reward_history.append(result.reward)

    return {
        "action": action.model_dump(),
        "result": result.model_dump(),
    }


@app.get("/analytics")
def analytics():
    total_reward = sum(reward_history)
    total_steps = len(reward_history)
    avg_reward = total_reward / total_steps if total_steps else 0.0

    return {
        "reward_history": reward_history,
        "total_reward": total_reward,
        "average_reward": avg_reward,
        "total_steps": total_steps,
    }