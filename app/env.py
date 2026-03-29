# app/env.py

from typing import List
from .models import Ticket, Action, Observation, StepResult, EpisodeState
from .utils import load_tickets, generate_episode_id
from .policies import validate_action
from .rewards import compute_reward


class SupportOpsEnv:
    def __init__(self, data_path: str = "data/tickets.json"):
        self.data_path = data_path
        self.tickets: List[Ticket] = []
        self.current_index: int = 0
        self.step_count: int = 0
        self.episode_id: str = ""
        self.done: bool = False

    def reset(self) -> StepResult:
        self.tickets = load_tickets(self.data_path)
        self.current_index = 0
        self.step_count = 0
        self.episode_id = generate_episode_id()
        self.done = False

        return StepResult(
            observation=self._get_observation("Environment reset successfully."),
            reward=0.0,
            done=False,
            info={"episode_id": self.episode_id}
        )

    def step(self, action: Action) -> StepResult:
        if self.done:
            return StepResult(
                observation=Observation(
                    message="Episode already finished.",
                    ticket=None,
                    available_actions=[]
                ),
                reward=0.0,
                done=True,
                info={}
            )

        ticket = self.tickets[self.current_index]
        self.step_count += 1

        valid, reason = validate_action(ticket, action)
        if not valid:
            return StepResult(
                observation=self._get_observation(f"Invalid action: {reason}"),
                reward=-2.0,
                done=False,
                info={"error": reason}
            )

        # Compute reward BEFORE changing ticket state
        reward = compute_reward(ticket, action)

        # Apply action AFTER grading
        self._apply_action(ticket, action)

        if self._is_ticket_completed(ticket):
            self.current_index += 1

        if self.current_index >= len(self.tickets):
            self.done = True
            return StepResult(
                observation=Observation(
                    message="All tickets processed successfully.",
                    ticket=None,
                    available_actions=[]
                ),
                reward=reward,
                done=True,
                info={"completed": True}
            )

        return StepResult(
            observation=self._get_observation("Action applied successfully."),
            reward=reward,
            done=False,
            info={"current_ticket_id": self.tickets[self.current_index].id}
        )

    def state(self) -> EpisodeState:
        resolved_count = sum(
            1 for t in self.tickets if t.status in ["resolved", "closed"]
        )

        return EpisodeState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            current_ticket_index=self.current_index,
            total_tickets=len(self.tickets),
            resolved_tickets=resolved_count
        )

    def _get_observation(self, message: str) -> Observation:
        if self.done or self.current_index >= len(self.tickets):
            return Observation(
                message=message,
                ticket=None,
                available_actions=[]
            )

        ticket = self.tickets[self.current_index]
        return Observation(
            message=message,
            ticket=ticket,
            available_actions=["classify", "assign", "respond", "resolve"]
        )

    def _apply_action(self, ticket: Ticket, action: Action) -> None:
        if action.action_type == "classify":
            ticket.category = action.payload["category"]

        elif action.action_type == "assign":
            ticket.assigned_to = action.payload["team"]
            ticket.status = "in_progress"

        elif action.action_type == "respond":
            ticket.response_sent = True

        elif action.action_type == "resolve":
            ticket.status = "resolved"
            ticket.resolution_note = action.payload["resolution_note"]

    def _is_ticket_completed(self, ticket: Ticket) -> bool:
        return ticket.status == "resolved"