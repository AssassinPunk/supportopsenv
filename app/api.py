from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

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


class ActionRequest(BaseModel):
    action_type: str
    ticket_id: int
    payload: Dict[str, Any] = {}


@app.get("/")
def root():
    return {"message": "SupportOpsEnv API is running"}


@app.post("/reset")
def reset_env():
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
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))