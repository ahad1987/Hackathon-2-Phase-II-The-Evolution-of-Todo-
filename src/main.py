#!/usr/bin/env python3
"""
Phase I - In-Memory Python Console Todo Application

A simple, deterministic CLI todo app with CRUD operations:
- Add tasks with title and optional description
- View all tasks with status indicators
- Update task title and/or description
- Delete tasks (IDs never reused)
- Mark tasks as complete/incomplete
- Exit command to terminate

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
import shlex
import sys


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
        return "✓" if self.status == TaskStatus.COMPLETE else "☐"


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
            raise ValueError("Provide new title or --desc <description>")

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

def parse_command(input_line: str) -> tuple:
    """
    Parse user input into command and arguments.

    Uses shlex to handle quoted strings correctly.

    Args:
        input_line (str): Raw user input

    Returns:
        tuple: (command, args) or (None, []) if invalid
    """
    try:
        parts = shlex.split(input_line.strip())
        if not parts:
            return None, []
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        return command, args
    except ValueError:
        # Mismatched quotes
        return None, []


def parse_task_id(value: str) -> int:
    """
    Parse and validate task ID.

    Args:
        value (str): String to parse

    Returns:
        int: Numeric task ID

    Raises:
        ValueError: If not numeric or invalid
    """
    try:
        task_id = int(value)
        if task_id <= 0:
            raise ValueError("Task ID must be positive")
        return task_id
    except ValueError:
        raise ValueError("Task ID must be numeric")


# ============================================================================
# CLI COMMAND HANDLERS
# ============================================================================

def handle_add(args, store: TodoStore) -> None:
    """
    Handle: add <title> [description]

    Adds a new task with auto-incremented ID.

    Test Scenarios:
    - add "Buy milk" → ID 1, status ☐, no description
    - add "Buy eggs" "Free-range" → ID 2, status ☐, with description
    - add (empty) → Error: "Title is required..."
    - add "x"*101 → Error: "Title exceeds 100 characters"
    """
    try:
        if len(args) < 1:
            print("Title is required. Usage: add <title> [description]")
            return

        title = args[0]
        description = args[1] if len(args) > 1 else None

        task = store.add_task(title, description)
        print(f"Task added with ID: {task.id}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def handle_list(args, store: TodoStore) -> None:
    """
    Handle: list

    Display all tasks with ID, status, title, and description.

    Test Scenarios:
    - list (3 tasks) → Show all 3 with correct IDs, status, titles
    - list (empty) → "No tasks yet. Add one with: add <title> [description]"
    - list (with complete task) → Show ✓ for complete, ☐ for incomplete
    """
    try:
        tasks = store.list_tasks()

        if not tasks:
            print("No tasks yet. Add one with: add <title> [description]")
            return

        # Display header
        print("\nID │ Status │ Title")
        print("───┼────────┼────────────────────────────────────")

        # Display each task
        for task in tasks:
            status = task.display_status()
            title = task.title[:30]  # Truncate for display
            desc_part = f" ({task.description[:30]}...)" if task.description else ""
            print(f" {task.id} │   {status}    │ {title}{desc_part}")

        print()

    except Exception as e:
        print(f"Error: {e}")


def handle_update(args, store: TodoStore) -> None:
    """
    Handle: update <id> [title] [--desc description]

    Update task title and/or description.

    Test Scenarios:
    - update 1 "New title" → Updated; ID/status unchanged
    - update 1 --desc "New desc" → Description updated
    - update 1 "Title" --desc "Desc" → Both updated
    - update 1 (no fields) → Error: "Provide new title or --desc..."
    - update 999 "Title" → Error: "Task ID 999 not found"
    """
    try:
        if len(args) < 1:
            print("Task ID is required. Usage: update <id> [title] [--desc description]")
            return

        task_id = parse_task_id(args[0])
        title = None
        description = None

        # Parse title and description from args
        if len(args) > 1:
            if args[1] == "--desc":
                if len(args) > 2:
                    description = args[2]
            else:
                title = args[1]
                if len(args) > 2 and args[2] == "--desc":
                    if len(args) > 3:
                        description = args[3]

        task = store.update_task(task_id, title, description)
        print(f"Task {task.id} updated")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def handle_delete(args, store: TodoStore) -> None:
    """
    Handle: delete <id>

    Delete task by ID. IDs are never reused.

    Test Scenarios:
    - delete 2 → "Task 2 deleted"; ID 2 removed
    - add after delete → New task gets next sequential ID (not 2)
    - delete 999 → Error: "Task ID 999 not found"
    - delete (no ID) → Error: "Task ID is required..."
    """
    try:
        if len(args) < 1:
            print("Task ID is required. Usage: delete <id>")
            return

        task_id = parse_task_id(args[0])
        store.delete_task(task_id)
        print(f"Task {task_id} deleted")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def handle_complete(args, store: TodoStore) -> None:
    """
    Handle: complete <id>

    Mark task as complete with ✓ indicator.

    Test Scenarios:
    - complete 1 → "Task 1 marked complete (✓)"
    - list → Task 1 shows ✓
    - complete (non-existent) → Error: "Task ID X not found"
    - complete (no ID) → Error: "Task ID is required..."
    """
    try:
        if len(args) < 1:
            print("Task ID is required. Usage: complete <id>")
            return

        task_id = parse_task_id(args[0])
        task = store.complete_task(task_id)
        print(f"Task {task.id} marked complete (✓)")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def handle_incomplete(args, store: TodoStore) -> None:
    """
    Handle: incomplete <id>

    Mark task as incomplete with ☐ indicator.

    Test Scenarios:
    - complete 1 → "Task 1 marked complete (✓)"
    - incomplete 1 → "Task 1 marked incomplete (☐)"
    - list → Task 1 shows ☐ again
    - incomplete (non-existent) → Error: "Task ID X not found"
    """
    try:
        if len(args) < 1:
            print("Task ID is required. Usage: incomplete <id>")
            return

        task_id = parse_task_id(args[0])
        task = store.incomplete_task(task_id)
        print(f"Task {task.id} marked incomplete (☐)")

    except ValueError as e:
        print(f"Error: {e}")
    except TaskNotFound as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def handle_exit(args, store: TodoStore) -> bool:
    """
    Handle: exit

    Terminate application. Data is lost (in-memory only).

    Test Scenarios:
    - exit → "Goodbye!" message; app terminates
    - Restart app → No tasks present (confirming in-memory only)
    """
    print("Goodbye!")
    return False  # Signal to break main loop


# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

def print_welcome_menu():
    """Display welcome menu with available commands."""
    print("""
Welcome to Todo App
Available commands:
  add <title> [description]       Add a new task
  list                            View all tasks
  update <id> [title] [--desc]    Update a task
  delete <id>                     Delete a task
  complete <id>                   Mark task as complete
  incomplete <id>                 Mark task as incomplete
  exit                            Exit the app
""")


def main():
    """
    Main application loop.

    Initialization:
    1. Create TodoStore (in-memory)
    2. Print welcome menu
    3. Loop: read input → parse → route → execute → error handling
    4. Exit on 'exit' command or Ctrl+C

    Test Workflow:
    - Start app → See welcome menu
    - add "Task 1" → Confirm "Task added with ID: 1"
    - add "Task 2" "with desc" → Confirm ID 2
    - list → See 2 tasks with ☐ status
    - update 1 "Updated Task 1" → Confirm updated
    - list → See updated task 1
    - complete 1 → Confirm "Task 1 marked complete (✓)"
    - list → See ✓ for task 1
    - delete 2 → Confirm "Task 2 deleted"
    - list → See only task 1
    - exit → "Goodbye!" and terminate
    - Restart app → No tasks (confirming in-memory reset)
    """
    store = TodoStore()
    print_welcome_menu()

    while True:
        try:
            # Read user input
            user_input = input("todo> ").strip()

            if not user_input:
                continue

            # Parse command and arguments
            command, args = parse_command(user_input)

            if command is None:
                print("Invalid input. Please try again.")
                continue

            # Route to appropriate handler
            if command == "add":
                handle_add(args, store)
            elif command == "list":
                handle_list(args, store)
            elif command == "update":
                handle_update(args, store)
            elif command == "delete":
                handle_delete(args, store)
            elif command == "complete":
                handle_complete(args, store)
            elif command == "incomplete":
                handle_incomplete(args, store)
            elif command == "exit":
                if not handle_exit(args, store):
                    break
            else:
                print(f"Unknown command '{command}'. Available: add, list, update, delete, complete, incomplete, exit")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
