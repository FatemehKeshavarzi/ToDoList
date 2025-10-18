import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from exceptions import ToDoError
from models.task import Task
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MAX_NUMBER_OF_TASKS_PER_PROJECT = int(os.getenv('MAX_NUMBER_OF_TASKS_PER_PROJECT'))

@dataclass
class Project:
    name: str
    description: Optional[str] = ''
    tasks: List[Task] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_task(self, task: Task):
        if len(self.tasks) >= MAX_NUMBER_OF_TASKS_PER_PROJECT:
            raise ToDoError(f"Maximum tasks per project: {MAX_NUMBER_OF_TASKS_PER_PROJECT}")
        if any(t.title == task.title for t in self.tasks):
            raise ToDoError("Task title already exists in this project.")
        self.tasks.append(task)

    def remove_task(self, task_title: str):
        for i, t in enumerate(self.tasks):
            if t.title == task_title:
                del self.tasks[i]
                return
        raise ToDoError("Task not found.")

    def get_task(self, task_title: str) -> Task:
        for t in self.tasks:
            if t.title == task_title:
                return t
        raise ToDoError("Task not found.")
