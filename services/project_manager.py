import os
from typing import Dict, List, Optional
from datetime import datetime
from exceptions import ToDoError
from models.project import Project
from models.task import Task
from dotenv import load_dotenv

# Load env vars
load_dotenv()
MAX_NUMBER_OF_PROJECTS = int(os.getenv('MAX_NUMBER_OF_PROJECTS'))

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
        del self.projects[name]

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

    # --- Task operations ---
    def add_task_to_project(self, project_name: str, title: str, description: str, deadline: str, status: str = 'todo') -> Task:
        proj = self.get_project(project_name)
        if not title.strip():
            raise ToDoError("Task title cannot be empty.")
        if len(title) > 30:
            raise ToDoError("Title must be less than 30 characters.")
        if len(description) > 150:
            raise ToDoError("Description must be less than 150 characters.")
        if not deadline.strip():
            raise ToDoError("Deadline is required and must be YYYY-MM-DD.")
        try:
            datetime.strptime(deadline, '%Y-%m-%d')
        except ValueError:
            raise ToDoError("Invalid deadline. Must be YYYY-MM-DD.")
        if status not in ('todo', 'doing', 'done'):
            raise ToDoError("Invalid status. Must be todo|doing|done.")
        task = Task(title=title, description=description, status=status, deadline=deadline)
        proj.add_task(task)
        return task

    def remove_task_from_project(self, project_name: str, task_title: str):
        proj = self.get_project(project_name)
        proj.remove_task(task_title)

    def update_task(self, project_name: str, task_title: str, new_title: Optional[str] = None,
                    new_description: Optional[str] = None, new_deadline: Optional[str] = None,
                    new_status: Optional[str] = None):
        task = self.get_project(project_name).get_task(task_title)
        if new_title:
            task.title = new_title.strip()
        if new_description is not None:
            task.description = new_description
        if new_deadline is not None:
            try:
                datetime.strptime(new_deadline, '%Y-%m-%d')
                task.deadline = new_deadline
            except ValueError:
                raise ToDoError("Invalid deadline format. Must be YYYY-MM-DD.")
        if new_status:
            task.mark_status(new_status)
