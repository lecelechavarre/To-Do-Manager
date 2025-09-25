from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    status: str = "pending"   # "pending" or "done"
    priority: str = "low"     # "low", "medium", "high"
    created_at: str = None    # ISO timestamp
    due_date: Optional[str] = None
    duration_seconds: int = 0
    remaining_seconds: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d: dict):
        # Provide robust defaults if keys are missing
        return Task(
            id=int(d.get("id", 0)),
            title=d.get("title", ""),
            description=d.get("description", ""),
            status=d.get("status", "pending"),
            priority=d.get("priority", "low"),
            created_at=d.get("created_at"),
            due_date=d.get("due_date"),
            duration_seconds=int(d.get("duration_seconds", 0)),
            remaining_seconds=int(d.get("remaining_seconds", d.get("duration_seconds", 0))),
        )
