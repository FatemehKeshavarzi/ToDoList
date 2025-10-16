import sys
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# ---- Exceptions ----
class ToDoError(Exception):
    """Custom exception for ToDo application errors."""

# ---- Models ----
@dataclass
class Task:
    title: str
    description: Optional[str] = ''
    status: str = 'todo'  # allowed: todo | doing | done
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    deadline: str = ''

    def mark_status(self, new_status: str):
        if new_status not in ('todo', 'doing', 'done'):
            raise ToDoError("Invalid status. Must be todo|doing|done.")
        self.status = new_status
