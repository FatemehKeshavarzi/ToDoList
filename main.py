import os
from services.project_manager import ProjectManager
from exceptions import ToDoError
from dotenv import load_dotenv

load_dotenv()
MAX_NUMBER_OF_PROJECTS = os.getenv('MAX_NUMBER_OF_PROJECTS')
MAX_NUMBER_OF_TASKS_PER_PROJECT = os.getenv('MAX_NUMBER_OF_TASKS_PER_PROJECT')

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
                print('Project updated.')
            elif choice == '10':
                print('Exit. Goodbye!')
                break
            else:
                print('Invalid selection.')
        except ToDoError as e:
            print('Error:', e)
        except Exception as e:
            print('Unexpected error:', e)

if __name__ == '__main__':
    manager = ProjectManager()
    print('ToDoList - in-memory version')
    print(f'MAX_NUMBER_OF_PROJECTS = {MAX_NUMBER_OF_PROJECTS}')
    print(f'MAX_NUMBER_OF_TASKS_PER_PROJECT = {MAX_NUMBER_OF_TASKS_PER_PROJECT}')
    cli_loop(manager)
