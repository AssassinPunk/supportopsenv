# app/utils.py

import json
import os
import uuid
from typing import List
from .models import Ticket
from .sample_data import SAMPLE_TICKETS


def generate_episode_id() -> str:
    return str(uuid.uuid4())


def load_tickets(file_path: str = "data/tickets.json") -> List[Ticket]:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = SAMPLE_TICKETS

    return [Ticket(**item) for item in raw]