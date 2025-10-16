import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

MAX_NUMBER_OF_PROJECTS = int(os.getenv('MAX_NUMBER_OF_PROJECTS'))
MAX_NUMBER_OF_TASKS_PER_PROJECT = int(os.getenv('MAX_NUMBER_OF_TASKS_PER_PROJECT'))

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
            
    # --- Task ---
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
            
# ---- CLI ----
def print_menu():
    print('=== ToDoList CLI ===')
    print('1. Create project')
    print('2. List projects')
    print('3. Delete project')
    print('4. Add task to project')
    print('5. List tasks in a project')
    print('6. Remove task from project')
    print('7. Update task (title/description/deadline/status)')
    print('8. Change task status')
    print('9. Update project (name/description)')
    print('10. Exit')

def cli_loop(manager: ProjectManager):
    while True:
        print_menu()
        choice = input('Select an option (number): ').strip()
        try:
            if choice == '1':
                name = input('Project name: ').strip()
                desc = input('Description (optional): ').strip()
                manager.create_project(name, desc)
                print('Project created.')
            elif choice == '2':
                projs = manager.list_projects()
                if not projs:
                    print('No projects.')
                else:
                    for p in projs:
                        print(f"- {p.name} (tasks: {len(p.tasks)}) - {p.description}")
            elif choice == '3':
                name = input('Project name to delete: ').strip()
                manager.delete_project(name)
                print('Project deleted.')
            elif choice == '4':
                pname = input('Project name: ').strip()
                title = input('Task title: ').strip()
                desc = input('Description: ').strip()
                deadline = input('Deadline YYYY-MM-DD: ').strip()
                status = input('Status (todo|doing|done) [default todo]: ').strip() or 'todo'
                manager.add_task_to_project(pname, title, desc, deadline, status)
                print('Task added.')
            elif choice == '5':
                pname = input('Project name: ').strip()
                proj = manager.get_project(pname)
                if not proj.tasks:
                    print('No tasks.')
                else:
                    for t in proj.tasks:
                        print(f"- {t.title} | status: {t.status} | created: {t.created_at} | deadline: {t.deadline}")
            elif choice == '6':
                pname = input('Project name: ').strip()
                ttitle = input('Task title to remove: ').strip()
                manager.remove_task_from_project(pname, ttitle)
                print('Task removed.')
            elif choice == '7':
                pname = input('Project name: ').strip()
                ttitle = input('Task title to update: ').strip()
                task = manager.get_project(pname).get_task(ttitle)
                new_title = input(f'New title (leave empty to keep "{task.title}"): ').strip()
                new_desc = input('New description (leave empty to keep current): ').strip()
                new_deadline = input(f'New deadline YYYY-MM-DD (leave empty to keep {task.deadline}): ').strip()
                new_status = input(f'New status (todo|doing|done) (leave empty to keep {task.status}): ').strip()
                manager.update_task(
                    pname, ttitle,
                    new_title=new_title or None,
                    new_description=new_desc or None,
                    new_deadline=new_deadline or None,
                    new_status=new_status or None
                )
                print('Task updated.')
            elif choice == '8':
                pname = input('Project name: ').strip()
                ttitle = input('Task title to change status: ').strip()
                task = manager.get_project(pname).get_task(ttitle)
                print(f'Current status: {task.status}')
                new_status = input('New status (todo|doing|done) [default todo]: ').strip() or 'todo'
                manager.update_task(pname, ttitle, new_status=new_status)
                print(f'Task "{task.title}" status changed to {task.status}.')
            elif choice == '9':
                current_name = input('Current project name: ').strip()
                proj = manager.get_project(current_name)
                print(f'Current name: {proj.name}')
                print(f'Current description: {proj.description}')
                new_name = input('New project name (leave empty to keep current): ').strip()
                new_desc = input('New description (leave empty to keep current): ').strip()
                manager.update_project(
                    current_name,
                    new_name=new_name or None,
                    new_description=new_desc or None
                )
                print('Project updated in-memory only.')
            elif choice == '10':
                print('Exit. Goodbye!')
                break
            else:
                print('Invalid selection.')
        except ToDoError as e:
            print('Error:', e)
        except Exception as e:
            print('Unexpected error:', e)

# ---- Entry point ----
if __name__ == '__main__':
    manager = ProjectManager()
    print('ToDoList - in-memory version')
    print(f'MAX_NUMBER_OF_PROJECTS = {MAX_NUMBER_OF_PROJECTS}')
    print(f'MAX_NUMBER_OF_TASKS_PER_PROJECT = {MAX_NUMBER_OF_TASKS_PER_PROJECT}')
    cli_loop(manager)            
        
           
