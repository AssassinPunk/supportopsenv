# app/models.py

from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


Priority = Literal["low", "medium", "high", "urgent"]
Status = Literal["open", "in_progress", "resolved", "closed"]
ActionType = Literal["classify", "assign", "respond", "resolve"]


class Ticket(BaseModel):
    id: int
    customer_name: str
    issue: str
    category: Optional[str] = None
    priority: Priority = "medium"
    status: Status = "open"
    assigned_to: Optional[str] = None
    response_sent: bool = False
    resolution_note: Optional[str] = None


class Action(BaseModel):
    action_type: ActionType
    ticket_id: int
    payload: Dict[str, Any] = Field(default_factory=dict)


class Observation(BaseModel):
    message: str
    ticket: Optional[Ticket] = None
    available_actions: List[str] = Field(default_factory=list)


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class EpisodeState(BaseModel):
    episode_id: str
    step_count: int
    current_ticket_index: int
    total_tickets: int
    resolved_tickets: int