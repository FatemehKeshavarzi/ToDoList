import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

MAX_NUMBER_OF_PROJECTS = int(os.getenv('MAX_NUMBER_OF_PROJECTS', 10))
MAX_NUMBER_OF_TASKS_PER_PROJECT = int(os.getenv('MAX_NUMBER_OF_TASKS_PER_PROJECT', 50))

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
    
# ---- Project Manager ----
class ProjectManager:
    def __init__(self):
        self.projects: Dict[str, Project] = {}

    # --- Project operations ---
    def create_project(self, name: str, description: str = '') -> Project:
        if not name or not name.strip():
            raise ToDoError("Project name cannot be empty.")
        if len(self.projects) >= MAX_NUMBER_OF_PROJECTS:
            raise ToDoError(f"Maximum number of projects: {MAX_NUMBER_OF_PROJECTS}")
        if name in self.projects:
            raise ToDoError("Project name already exists.")
        proj = Project(name=name, description=description)
        self.projects[name] = proj
        return proj

    def delete_project(self, name: str):
        if name not in self.projects:
            raise ToDoError("Project not found.")
        del self.projects[name]  # cascade delete

    def list_projects(self) -> List[Project]:
        return list(self.projects.values())

    def get_project(self, name: str) -> Project:
        if name not in self.projects:
            raise ToDoError("Project not found.")
        return self.projects[name]

    def update_project(self, current_name: str, new_name: Optional[str] = None, new_description: Optional[str] = None):
        if current_name not in self.projects:
            raise ToDoError("Project not found.")
        proj = self.projects[current_name]

        if new_name is not None:
            clean_new = new_name.strip()
            if not clean_new:
                raise ToDoError("New project name cannot be empty.")
            if clean_new != current_name and clean_new in self.projects:
                raise ToDoError("Another project with the new name already exists.")
            if clean_new != current_name:
                proj.name = clean_new
                self.projects[clean_new] = proj
                del self.projects[current_name]

        if new_description is not None:
            proj.description = new_description
           
