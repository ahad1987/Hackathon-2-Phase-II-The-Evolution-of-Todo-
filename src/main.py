#!/usr/bin/env python3
"""
Phase I - In-Memory Python Console Todo Application

A menu-driven CLI todo app with numeric choices (1-7):
1. Add Task - Create new task with title and description
2. View All Tasks - Display all tasks with status indicators
3. Update Task - Modify task title and/or description
4. Delete Task - Remove task by ID
5. Mark Task Completed - Mark task as complete (✓ shown in list)
6. Mark Task Incomplete - Mark task as incomplete (☐ shown in list)
7. Exit - Terminate application

All data is in-memory only; resets on application exit.

Technical Stack:
- Python 3.13+
- Standard library only (no external dependencies)
- Synchronous, single-process execution
- stdin/stdout for I/O

Constitution Compliance:
- Correctness: All logic works exactly as specified
- Simplicity: Clean, minimal, readable code
- Determinism: Predictable behavior; no hidden side effects
- Spec-Driven: Implementation strictly follows requirements
- Incremental Design: Modular, extensible for Phase II
"""

from datetime import datetime
from enum import Enum


# ============================================================================
# DOMAIN MODEL: Task Entity
# ============================================================================

class TaskStatus(Enum):
    """Task status enumeration."""
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class Task:
    """
    Represents a single todo item.

    Attributes:
        id (int): Auto-incremented unique identifier; never reused
        title (str): Task title (1-100 characters)
        description (str): Optional task description (0-500 characters)
        status (TaskStatus): Current status (incomplete or complete)
        created_at (datetime): When the task was created
    """

    def __init__(self, task_id: int, title: str, description: str = None):
        """
        Initialize a new task.

        Args:
            task_id (int): Auto-incremented ID
            title (str): Task title
            description (str, optional): Task description
        """
        self.id = task_id
        self.title = title
        self.description = description if description else ""
        self.status = TaskStatus.INCOMPLETE
        self.created_at = datetime.now()

    def mark_complete(self):
        """Mark task as complete."""
        self.status = TaskStatus.COMPLETE

    def mark_incomplete(self):
        """Mark task as incomplete."""
        self.status = TaskStatus.INCOMPLETE

    def display_status(self) -> str:
        """Return visual status indicator."""
        return "[*]" if self.status == TaskStatus.COMPLETE else "[ ]"


# ============================================================================
# STORAGE LAYER: TodoStore
# ============================================================================

class TaskNotFound(Exception):
    """Raised when task ID doesn't exist."""
    pass


class InvalidTaskID(Exception):
    """Raised when task ID is invalid."""
    pass


class TodoStore:
    """
    In-memory storage for tasks.

    Manages tasks dict and sequential ID generation.
    Never reuses deleted IDs.
    """

    def __init__(self):
        """Initialize empty task store."""
        self.tasks = {}  # {id: Task}
        self.next_id = 1

    def add_task(self, title: str, description: str = None) -> Task:
        """
        Add a new task.

        Args:
            title (str): Task title (required)
            description (str, optional): Task description

        Returns:
            Task: The created task

        Raises:
            ValueError: If title is empty or exceeds max length
        """
        self._validate_title(title)
        if description:
            self._validate_description(description)

        task = Task(self.next_id, title.strip(), description.strip() if description else None)
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def get_task(self, task_id: int) -> Task:
        """
        Get task by ID.

        Args:
            task_id (int): Task ID

        Returns:
            Task: The task if found

        Raises:
            TaskNotFound: If task doesn't exist
        """
        if task_id not in self.tasks:
            raise TaskNotFound(f"Task ID {task_id} not found")
        return self.tasks[task_id]

    def list_tasks(self) -> list:
        """Return all tasks in order."""
        return list(self.tasks.values())

    def update_task(self, task_id: int, title: str = None, description: str = None) -> Task:
        """
        Update task title and/or description.

        Args:
            task_id (int): Task ID
            title (str, optional): New title
            description (str, optional): New description

        Returns:
            Task: The updated task

        Raises:
            TaskNotFound: If task doesn't exist
            ValueError: If neither title nor description provided
        """
        if title is None and description is None:
            raise ValueError("Provide new title or description")

        task = self.get_task(task_id)

        if title:
            self._validate_title(title)
            task.title = title.strip()

        if description is not None:
            self._validate_description(description)
            task.description = description.strip()

        return task

    def delete_task(self, task_id: int) -> None:
        """
        Delete task by ID.

        Args:
            task_id (int): Task ID

        Raises:
            TaskNotFound: If task doesn't exist

        Note: next_id is NOT decremented; IDs continue sequentially.
        """
        if task_id not in self.tasks:
            raise TaskNotFound(f"Task ID {task_id} not found")
        del self.tasks[task_id]

    def complete_task(self, task_id: int) -> Task:
        """
        Mark task as complete.

        Args:
            task_id (int): Task ID

        Returns:
            Task: The updated task

        Raises:
            TaskNotFound: If task doesn't exist
        """
        task = self.get_task(task_id)
        task.mark_complete()
        return task

    def incomplete_task(self, task_id: int) -> Task:
        """
        Mark task as incomplete.

        Args:
            task_id (int): Task ID

        Returns:
            Task: The updated task

        Raises:
            TaskNotFound: If task doesn't exist
        """
        task = self.get_task(task_id)
        task.mark_incomplete()
        return task

    @staticmethod
    def _validate_title(title: str) -> None:
        """Validate task title."""
        title = title.strip() if title else ""
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 100:
            raise ValueError("Title exceeds 100 characters")

    @staticmethod
    def _validate_description(description: str) -> None:
        """Validate task description."""
        if len(description) > 500:
            raise ValueError("Description exceeds 500 characters")


# ============================================================================
# VALIDATION LAYER
# ============================================================================

def safe_input(prompt: str) -> str:
    """
    Safely read input from user.

    Args:
        prompt (str): Prompt to display

    Returns:
        str: User input (stripped)
    """
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def safe_int_input(prompt: str) -> int:
    """
    Safely read integer input from user.

    Args:
        prompt (str): Prompt to display

    Returns:
        int: User input as integer, or -1 if invalid

    Raises:
        ValueError: If input is not numeric
    """
    try:
        value = safe_input(prompt)
        return int(value)
    except ValueError:
        raise ValueError("Invalid input: must be a number")


# ============================================================================
# MENU OPERATIONS
# ============================================================================

def menu_add_task(store: TodoStore) -> None:
    """
    Menu operation 1: Add a new task.

    Prompts user for title and optional description.
    """
    print("\n" + "=" * 60)
    print("OPTION 1: ADD TASK")
    print("=" * 60)

    try:
        title = safe_input("Enter task title: ")
        if not title:
            print("Error: Title cannot be empty")
            return

        description = safe_input("Enter task description (optional, press Enter to skip): ")

        task = store.add_task(title, description)
        print(f"\nSuccess! Task added with ID: {task.id}")
        print(f"  Title: {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        print(f"  Status: {task.display_status()} Incomplete")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def menu_list_tasks(store: TodoStore) -> None:
    """
    Menu operation 2: View all tasks.

    Displays all tasks with ID, status, title, and description.
    """
    print("\n" + "=" * 60)
    print("OPTION 2: VIEW ALL TASKS")
    print("=" * 60)

    try:
        tasks = store.list_tasks()

        if not tasks:
            print("\nNo tasks yet. Use option 1 to add your first task!")
            return

        print(f"\nTotal tasks: {len(tasks)}\n")
        print("ID | Status   | Title")
        print("---+----------+------------------------------------")

        for task in tasks:
            status = task.display_status()
            title = task.title[:40]  # Truncate for display
            desc_part = f" ({task.description[:30]}...)" if task.description else ""
            print(f" {task.id:2d} | {status:8s} | {title}{desc_part}")

        print()

    except Exception as e:
        print(f"Error: {e}")


def menu_update_task(store: TodoStore) -> None:
    """
    Menu operation 3: Update an existing task.

    Prompts user for task ID and new title/description.
    """
    print("\n" + "=" * 60)
    print("OPTION 3: UPDATE TASK")
    print("=" * 60)

    try:
        task_id = safe_int_input("Enter task ID to update: ")

        # Verify task exists
        task = store.get_task(task_id)
        print(f"\nCurrent task: {task.title}")
        if task.description:
            print(f"Description: {task.description}")

        new_title = safe_input("\nEnter new title (press Enter to keep current): ")
        new_description = safe_input("Enter new description (press Enter to keep current): ")

        if not new_title and not new_description:
            print("Error: You must provide either a new title or description")
            return

        updated_task = store.update_task(
            task_id,
            title=new_title if new_title else None,
            description=new_description if new_description else None
        )

        print(f"\nSuccess! Task {updated_task.id} updated")
        print(f"  New title: {updated_task.title}")
        print(f"  New description: {updated_task.description if updated_task.description else '(none)'}")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def menu_delete_task(store: TodoStore) -> None:
    """
    Menu operation 4: Delete a task.

    Prompts user for task ID to delete.
    """
    print("\n" + "=" * 60)
    print("OPTION 4: DELETE TASK")
    print("=" * 60)

    try:
        task_id = safe_int_input("Enter task ID to delete: ")

        # Verify task exists first
        task = store.get_task(task_id)
        print(f"\nTask to delete: {task.title}")

        confirm = safe_input("Are you sure? (yes/no): ").lower()
        if confirm not in ['yes', 'y']:
            print("Deletion cancelled")
            return

        store.delete_task(task_id)
        print(f"\nSuccess! Task {task_id} deleted")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def menu_complete_task(store: TodoStore) -> None:
    """
    Menu operation 5: Mark a task as completed.

    Prompts user for task ID to mark complete.
    """
    print("\n" + "=" * 60)
    print("OPTION 5: MARK TASK COMPLETED")
    print("=" * 60)

    try:
        task_id = safe_int_input("Enter task ID to mark as completed: ")

        task = store.complete_task(task_id)
        print(f"\nSuccess! Task {task.id} marked complete {task.display_status()}")
        print(f"  Title: {task.title}")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def menu_incomplete_task(store: TodoStore) -> None:
    """
    Menu operation 6: Mark a task as incomplete.

    Prompts user for task ID to mark incomplete.
    """
    print("\n" + "=" * 60)
    print("OPTION 6: MARK TASK INCOMPLETE")
    print("=" * 60)

    try:
        task_id = safe_int_input("Enter task ID to mark as incomplete: ")

        task = store.incomplete_task(task_id)
        print(f"\nSuccess! Task {task.id} marked incomplete {task.display_status()}")
        print(f"  Title: {task.title}")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("TODO APPLICATION - MAIN MENU")
    print("=" * 60)
    print("\nPlease select an option (1-7):\n")
    print("  1. Add Task")
    print("  2. View All Tasks")
    print("  3. Update Task")
    print("  4. Delete Task")
    print("  5. Mark Task Completed")
    print("  6. Mark Task Incomplete")
    print("  7. Exit")
    print()


# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

def main():
    """
    Main application loop with numeric menu selection.

    Displays menu (1-7) and executes selected operation.
    Continues until user selects option 7 (Exit).
    """
    store = TodoStore()

    print("\n" + "=" * 60)
    print("WELCOME TO TODO APPLICATION")
    print("=" * 60)
    print("\nThis is an in-memory task management system.")
    print("Data will be lost when you exit the application.")

    while True:
        try:
            print_menu()

            choice = safe_input("Choice selection 1-7: ").strip()

            if choice == "1":
                menu_add_task(store)
            elif choice == "2":
                menu_list_tasks(store)
            elif choice == "3":
                menu_update_task(store)
            elif choice == "4":
                menu_delete_task(store)
            elif choice == "5":
                menu_complete_task(store)
            elif choice == "6":
                menu_incomplete_task(store)
            elif choice == "7":
                print("\n" + "=" * 60)
                print("Thank you for using Todo Application!")
                print("=" * 60)
                print("\nGoodbye!\n")
                break
            else:
                print(f"\nError: Invalid choice '{choice}'. Please enter 1-7.")

        except KeyboardInterrupt:
            print("\n\nApplication terminated by user.")
            print("Goodbye!\n")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
