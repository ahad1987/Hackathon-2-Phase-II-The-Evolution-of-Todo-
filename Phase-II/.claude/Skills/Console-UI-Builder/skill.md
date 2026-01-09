# Console UI Builder Agent - Professional Skill Profile

## Role Definition
**Console UI Builder Agent** specialized in designing and building production-grade console-based user interfaces with clear navigation, readable layouts, and cross-platform terminal compatibility.

---

## Core Responsibilities

### 1. Screen Design & Layout
- Design clear, readable console screens
- Structure information hierarchies
- Implement consistent spacing and alignment
- Create visually distinct sections
- Balance information density with readability
- Design for various terminal sizes

### 2. Menu Systems & Navigation
- Build intuitive menu structures
- Implement keyboard navigation
- Create breadcrumb trails
- Design tab interfaces
- Support hotkeys and shortcuts
- Enable back/forward navigation

### 3. Interactive Flows
- Design wizard-style workflows
- Implement form inputs and validation
- Create selection interfaces (single/multi-select)
- Build search and filter interfaces
- Design confirmation dialogs
- Handle cancellation and escape flows

### 4. Text Rendering & Formatting
- Render tables with proper alignment
- Display lists and hierarchies
- Format text with colors and styles
- Implement word wrapping
- Create ASCII art and borders
- Support Unicode characters

### 5. Input Handling
- Capture keyboard input (keys, combinations)
- Handle mouse events (when supported)
- Validate input in real-time
- Provide autocomplete suggestions
- Support clipboard operations
- Handle special keys (arrows, function keys)

### 6. Feedback & Status Display
- Show loading spinners and progress bars
- Display success/error/warning messages
- Implement toast notifications
- Create status indicators
- Show real-time updates
- Provide context-sensitive help

### 7. Error Handling & Validation
- Display clear error messages
- Highlight invalid input fields
- Show validation feedback
- Provide correction suggestions
- Handle edge cases gracefully
- Support error recovery

### 8. Accessibility Features
- Support screen readers (where possible)
- Provide keyboard-only navigation
- Use high-contrast color schemes
- Support terminal size adjustments
- Implement text-only fallbacks
- Follow accessibility guidelines

### 9. Cross-Platform Compatibility
- Work on Windows, macOS, Linux
- Handle different terminal emulators
- Support various color modes
- Adapt to terminal capabilities
- Test on common environments
- Provide fallbacks for unsupported features

### 10. Modularity & Maintainability
- Separate UI logic from business logic
- Create reusable components
- Implement state management
- Support theming and customization
- Enable testing and mocking
- Document component APIs

---

## Technical Stack

### Core Libraries

#### Rich (Recommended - Python)
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live

console = Console()

# Rich features:
# - Colors and styles
# - Tables and panels
# - Progress bars
# - Live updates
# - Markdown rendering
# - Syntax highlighting
```

#### Blessed (Python)
```python
from blessed import Terminal

term = Terminal()

# Blessed features:
# - Terminal capabilities detection
# - Color support
# - Cursor positioning
# - Keyboard input
# - Full-screen apps
```

#### Prompt Toolkit (Python)
```python
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import TextArea, Frame

# Prompt Toolkit features:
# - Full-featured TUI framework
# - Syntax highlighting
# - Autocompletion
# - Mouse support
# - Custom key bindings
```

#### Textual (Python - Modern TUI)
```python
from textual.app import App
from textual.widgets import Header, Footer, Button, DataTable

# Textual features:
# - Reactive components
# - CSS-like styling
# - Event handling
# - Widget library
# - Async support
```

#### Bubbletea (Go)
```go
import tea "github.com/charmbracelet/bubbletea"

// Bubbletea features:
// - Elm architecture (Model-Update-View)
// - Composable components
// - Event-driven
// - Terminal rendering
```

#### Inquirer/Inquirer.js (Node.js)
```javascript
const inquirer = require('inquirer');

// Inquirer features:
// - Interactive prompts
// - Input validation
// - Multiple question types
// - Extensible
```

### Supporting Libraries
```python
# Colors and Styling
import colorama          # Cross-platform color support
from termcolor import colored  # Simple colored output

# Terminal Control
import curses           # Low-level terminal control (Unix)
import blessed          # High-level terminal wrapper

# Progress and Spinners
from tqdm import tqdm   # Progress bars
from halo import Halo   # Spinners

# Tables and Data Display
from tabulate import tabulate  # Simple tables
from prettytable import PrettyTable  # Formatted tables

# Input and Forms
import click            # CLI framework with prompts
import inquirer         # Interactive prompts

# Terminal Information
import shutil           # Get terminal size
import os              # Environment variables
```

---

## Console UI Architecture

### Project Structure
```
console-app/
├── README.md
├── requirements.txt
├── setup.py
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration
│   ├── ui/                  # UI components
│   │   ├── __init__.py
│   │   ├── components/      # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── menu.py
│   │   │   ├── table.py
│   │   │   ├── form.py
│   │   │   ├── dialog.py
│   │   │   └── progress.py
│   │   ├── screens/         # Full screens
│   │   │   ├── __init__.py
│   │   │   ├── home.py
│   │   │   ├── settings.py
│   │   │   └── details.py
│   │   ├── layouts/         # Layout templates
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── dashboard.py
│   │   └── theme.py         # Theme and styling
│   ├── core/                # Business logic
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── services.py
│   │   └── utils.py
│   └── state.py             # Application state
└── tests/
    ├── __init__.py
    ├── test_ui.py
    └── test_components.py
```

### Component Architecture
```python
# app/ui/components/base.py
"""
Base component class for all UI components.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from rich.console import Console, RenderableType


class Component(ABC):
    """Base class for all UI components."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.visible = True
        self.enabled = True
        self._state: Dict[str, Any] = {}
    
    @abstractmethod
    def render(self) -> RenderableType:
        """Render the component. Returns a Rich renderable."""
        pass
    
    def show(self):
        """Display the component."""
        if self.visible:
            self.console.print(self.render())
    
    def update_state(self, **kwargs):
        """Update component state."""
        self._state.update(kwargs)
        self.refresh()
    
    def refresh(self):
        """Refresh the component display."""
        self.console.clear()
        self.show()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get component state value."""
        return self._state.get(key, default)
```

---

## Core UI Components

### 1. Menu Component
```python
# app/ui/components/menu.py
"""
Interactive menu component with keyboard navigation.
"""

from typing import List, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import readchar


class MenuItem:
    """Menu item with action."""
    
    def __init__(
        self,
        label: str,
        action: Optional[Callable] = None,
        hotkey: Optional[str] = None,
        submenu: Optional['Menu'] = None
    ):
        self.label = label
        self.action = action
        self.hotkey = hotkey
        self.submenu = submenu
        self.enabled = True


class Menu:
    """Interactive menu with navigation."""
    
    def __init__(
        self,
        title: str,
        items: List[MenuItem],
        console: Optional[Console] = None
    ):
        self.title = title
        self.items = items
        self.console = console or Console()
        self.selected_index = 0
    
    def render(self) -> Panel:
        """Render menu as a panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Hotkey", style="cyan")
        table.add_column("Option")
        
        for idx, item in enumerate(self.items):
            # Highlight selected item
            if idx == self.selected_index:
                style = "bold white on blue"
                pointer = "► "
            else:
                style = "white" if item.enabled else "dim"
                pointer = "  "
            
            hotkey = f"[{item.hotkey}]" if item.hotkey else ""
            label = Text(f"{pointer}{item.label}", style=style)
            
            table.add_row(hotkey, label)
        
        return Panel(
            table,
            title=f"[bold]{self.title}[/bold]",
            border_style="blue"
        )
    
    def show(self) -> Optional[MenuItem]:
        """Display menu and handle navigation."""
        while True:
            self.console.clear()
            self.console.print(self.render())
            self.console.print("\n[dim]↑↓: Navigate | Enter: Select | Q: Quit[/dim]")
            
            key = readchar.readkey()
            
            if key == readchar.key.UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            
            elif key == readchar.key.DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            
            elif key == readchar.key.ENTER:
                selected_item = self.items[self.selected_index]
                if selected_item.enabled:
                    if selected_item.submenu:
                        result = selected_item.submenu.show()
                        if result:
                            return result
                    elif selected_item.action:
                        selected_item.action()
                    return selected_item
            
            elif key.lower() == 'q':
                return None
            
            # Check hotkeys
            else:
                for item in self.items:
                    if item.hotkey and key.lower() == item.hotkey.lower():
                        if item.enabled:
                            if item.action:
                                item.action()
                            return item


# Usage Example
def create_main_menu() -> Menu:
    """Create the main application menu."""
    
    def view_records():
        console.print("[green]Viewing records...[/green]")
    
    def add_record():
        console.print("[green]Adding new record...[/green]")
    
    def settings():
        console.print("[blue]Opening settings...[/blue]")
    
    items = [
        MenuItem("View Records", action=view_records, hotkey="v"),
        MenuItem("Add Record", action=add_record, hotkey="a"),
        MenuItem("Settings", action=settings, hotkey="s"),
        MenuItem("Exit", action=None, hotkey="x"),
    ]
    
    return Menu("Main Menu", items)
```

### 2. Table Component
```python
# app/ui/components/table.py
"""
Data table component with sorting and pagination.
"""

from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table as RichTable
from rich.panel import Panel


class DataTable:
    """Paginated data table with sorting."""
    
    def __init__(
        self,
        columns: List[str],
        data: List[Dict[str, Any]],
        title: Optional[str] = None,
        page_size: int = 10,
        console: Optional[Console] = None
    ):
        self.columns = columns
        self.data = data
        self.title = title
        self.page_size = page_size
        self.console = console or Console()
        self.current_page = 0
        self.sort_column: Optional[str] = None
        self.sort_reverse = False
    
    def render(self) -> Panel:
        """Render the table."""
        # Sort data if needed
        sorted_data = self.data
        if self.sort_column:
            sorted_data = sorted(
                self.data,
                key=lambda x: x.get(self.sort_column, ''),
                reverse=self.sort_reverse
            )
        
        # Paginate
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_data = sorted_data[start_idx:end_idx]
        
        # Create table
        table = RichTable(show_header=True, header_style="bold cyan")
        
        for col in self.columns:
            # Add sort indicator
            header = col
            if col == self.sort_column:
                header += " ↓" if self.sort_reverse else " ↑"
            table.add_column(header)
        
        # Add rows
        for row in page_data:
            table.add_row(*[str(row.get(col, '')) for col in self.columns])
        
        # Add pagination info
        total_pages = (len(sorted_data) - 1) // self.page_size + 1
        footer = f"Page {self.current_page + 1} of {total_pages} | Total: {len(sorted_data)} rows"
        
        return Panel(
            table,
            title=f"[bold]{self.title}[/bold]" if self.title else None,
            subtitle=footer,
            border_style="blue"
        )
    
    def show(self):
        """Display table with navigation."""
        while True:
            self.console.clear()
            self.console.print(self.render())
            self.console.print("\n[dim]← →: Pages | S: Sort | Q: Back[/dim]")
            
            key = readchar.readkey()
            
            if key == readchar.key.LEFT:
                self.previous_page()
            elif key == readchar.key.RIGHT:
                self.next_page()
            elif key.lower() == 's':
                self.sort_prompt()
            elif key.lower() == 'q':
                break
    
    def next_page(self):
        """Navigate to next page."""
        total_pages = (len(self.data) - 1) // self.page_size + 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
    
    def previous_page(self):
        """Navigate to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
    
    def sort_prompt(self):
        """Prompt for sort column."""
        from rich.prompt import Prompt
        
        self.console.print("\nAvailable columns:")
        for idx, col in enumerate(self.columns, 1):
            self.console.print(f"  {idx}. {col}")
        
        choice = Prompt.ask(
            "Enter column number to sort by",
            choices=[str(i) for i in range(1, len(self.columns) + 1)]
        )
        
        self.sort_column = self.columns[int(choice) - 1]
        self.sort_reverse = not self.sort_reverse


# Usage Example
def display_users_table():
    """Display users in a table."""
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "Admin"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "User"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "User"},
    ]
    
    table = DataTable(
        columns=["id", "name", "email", "role"],
        data=users,
        title="User Management",
        page_size=10
    )
    
    table.show()
```

### 3. Form Component
```python
# app/ui/components/form.py
"""
Interactive form component with validation.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text


@dataclass
class FormField:
    """Form field definition."""
    
    name: str
    label: str
    field_type: str = "text"  # text, number, email, password, choice
    required: bool = True
    default: Optional[Any] = None
    choices: Optional[List[str]] = None
    validator: Optional[Callable[[Any], bool]] = None
    error_message: str = "Invalid input"


class Form:
    """Interactive form with validation."""
    
    def __init__(
        self,
        title: str,
        fields: List[FormField],
        console: Optional[Console] = None
    ):
        self.title = title
        self.fields = fields
        self.console = console or Console()
        self.values: Dict[str, Any] = {}
        self.errors: Dict[str, str] = {}
    
    def render_field(self, field: FormField, show_error: bool = False) -> Panel:
        """Render a single form field."""
        content = Text()
        
        # Field label
        required_marker = "*" if field.required else ""
        content.append(f"{field.label}{required_marker}\n", style="bold")
        
        # Current value
        current_value = self.values.get(field.name, field.default)
        if current_value is not None:
            content.append(f"Current: {current_value}\n", style="dim")
        
        # Error message
        if show_error and field.name in self.errors:
            content.append(f"\n❌ {self.errors[field.name]}", style="bold red")
        
        return Panel(content, border_style="yellow" if show_error else "blue")
    
    def validate_field(self, field: FormField, value: Any) -> bool:
        """Validate a field value."""
        # Check required
        if field.required and (value is None or value == ""):
            self.errors[field.name] = "This field is required"
            return False
        
        # Check type
        if field.field_type == "number":
            try:
                float(value)
            except (ValueError, TypeError):
                self.errors[field.name] = "Must be a number"
                return False
        
        elif field.field_type == "email":
            if "@" not in str(value):
                self.errors[field.name] = "Must be a valid email"
                return False
        
        # Custom validator
        if field.validator and value:
            if not field.validator(value):
                self.errors[field.name] = field.error_message
                return False
        
        # Clear error if valid
        self.errors.pop(field.name, None)
        return True
    
    def show(self) -> Optional[Dict[str, Any]]:
        """Display form and collect input."""
        self.console.clear()
        self.console.print(f"\n[bold blue]{self.title}[/bold blue]\n")
        
        for field in self.fields:
            while True:
                # Display field
                self.console.print(self.render_field(
                    field,
                    show_error=field.name in self.errors
                ))
                
                # Get input based on field type
                if field.field_type == "choice" and field.choices:
                    value = Prompt.ask(
                        f"Select {field.label}",
                        choices=field.choices,
                        default=field.default
                    )
                
                elif field.field_type == "password":
                    value = Prompt.ask(
                        f"Enter {field.label}",
                        password=True
                    )
                
                elif field.field_type == "confirm":
                    value = Confirm.ask(
                        f"{field.label}",
                        default=field.default or False
                    )
                
                else:
                    value = Prompt.ask(
                        f"Enter {field.label}",
                        default=str(field.default) if field.default else None
                    )
                
                # Validate
                if self.validate_field(field, value):
                    self.values[field.name] = value
                    break
                else:
                    self.console.print(
                        f"[red]❌ {self.errors[field.name]}[/red]"
                    )
                    if not Confirm.ask("Try again?", default=True):
                        return None
        
        # Show summary and confirm
        self.console.clear()
        self.show_summary()
        
        if Confirm.ask("\nSubmit form?", default=True):
            return self.values
        else:
            return None
    
    def show_summary(self):
        """Display form summary."""
        from rich.table import Table
        
        table = Table(title=f"{self.title} - Summary", show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        for field in self.fields:
            value = self.values.get(field.name, "")
            # Hide password values
            if field.field_type == "password":
                value = "••••••••"
            table.add_row(field.label, str(value))
        
        self.console.print(table)


# Usage Example
def create_user_form():
    """Create a user registration form."""
    
    def validate_username(value):
        """Validate username format."""
        return len(value) >= 3 and value.isalnum()
    
    fields = [
        FormField(
            name="username",
            label="Username",
            required=True,
            validator=validate_username,
            error_message="Username must be at least 3 alphanumeric characters"
        ),
        FormField(
            name="email",
            label="Email",
            field_type="email",
            required=True
        ),
        FormField(
            name="password",
            label="Password",
            field_type="password",
            required=True
        ),
        FormField(
            name="role",
            label="Role",
            field_type="choice",
            choices=["admin", "user", "guest"],
            default="user"
        ),
        FormField(
            name="active",
            label="Active User",
            field_type="confirm",
            default=True
        ),
    ]
    
    form = Form("User Registration", fields)
    result = form.show()
    
    if result:
        console.print("\n[green]✓ Form submitted successfully![/green]")
        console.print(result)
```

### 4. Progress Component
```python
# app/ui/components/progress.py
"""
Progress indicators and spinners.
"""

from typing import Optional, Callable, Iterable
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    TaskProgressColumn
)
from rich.live import Live
from rich.spinner import Spinner
import time


class ProgressIndicator:
    """Progress bar and spinner wrapper."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def show_spinner(self, text: str, task: Callable):
        """Show spinner while task executes."""
        with self.console.status(f"[bold blue]{text}...") as status:
            result = task()
            status.stop()
            return result
    
    def show_progress(
        self,
        items: Iterable,
        description: str = "Processing",
        total: Optional[int] = None
    ):
        """Show progress bar for iterable."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(description, total=total or len(items))
            
            for item in items:
                yield item
                progress.update(task, advance=1)
    
    def multi_progress(self, tasks: list):
        """Show multiple progress bars."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            task_ids = {}
            for task_name, total in tasks:
                task_ids[task_name] = progress.add_task(task_name, total=total)
            
            yield progress, task_ids


# Usage Example
def process_files_with_progress():
    """Process files with progress bar."""
    files = ["file1.txt", "file2.txt", "file3.txt"]
    
    progress = ProgressIndicator()
    
    for file in progress.show_progress(files, "Processing files"):
        time.sleep(0.5)  # Simulate processing
        console.print(f"Processed {file}")


def multi_task_example():
    """Multiple concurrent progress bars."""
    progress = ProgressIndicator()
    
    tasks = [
        ("Downloading", 100),
        ("Processing", 50),
        ("Uploading", 75)
    ]
    
    with progress.multi_progress(tasks) as (prog, task_ids):
        # Simulate work
        for i in range(100):
            if i < 100:
                prog.update(task_ids["Downloading"], advance=1)
            if i < 50:
                prog.update(task_ids["Processing"], advance=1)
            if i < 75:
                prog.update(task_ids["Uploading"], advance=1)
            time.sleep(0.05)
```

### 5. Dialog Component
```python
# app/ui/components/dialog.py
"""
Dialog boxes for confirmations, alerts, and prompts.
"""

from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text


class Dialog:
    """Dialog box component."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def alert(
        self,
        title: str,
        message: str,
        alert_type: str = "info"  # info, success, warning, error
    ):
        """Show an alert dialog."""
        # Select style and icon based on type
        styles = {
            "info": ("blue", "ℹ"),
            "success": ("green", "✓"),
            "warning": ("yellow", "⚠"),
            "error": ("red", "✗")
        }
        
        style, icon = styles.get(alert_type, styles["info"])
        
        content = Text()
        content.append(f"{icon} ", style=f"bold {style}")
        content.append(message)
        
        panel = Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
        
        Prompt.ask("Press Enter to continue", default="")
    
    def confirm(
        self,
        title: str,
        message: str,
        default: bool = False
    ) -> bool:
        """Show confirmation dialog."""
        panel = Panel(
            f"❓ {message}",
            title=f"[bold yellow]{title}[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        
        return Confirm.ask("Continue?", default=default)
    
    def choice(
        self,
        title: str,
        message: str,
        choices: List[str],
        default: Optional[str] = None
    ) -> str:
        """Show choice dialog."""
        content = Text()
        content.append(f"{message}\n\n", style="white")
        
        for idx, choice in enumerate(choices, 1):
            content.append(f"{idx}. {choice}\n", style="cyan")
        
        panel = Panel(
            content,
            title=f"[bold blue]{title}[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        
        return Prompt.ask(
            "Select an option",
            choices=[str(i) for i in range(1, len(choices) + 1)],
            default=default
        )
    
    def input(
        self,
        title: str,
        message: str,
        default: Optional[str] = None,
        password: bool = False
    ) -> str:
        """Show input dialog."""
        panel = Panel(
            f"✎ {message}",
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        
        return Prompt.ask(
            "Enter value",
            default=default,
            password=password
        )


# Usage Example
def dialog_examples():
    """Demonstrate dialog usage."""
    dialog = Dialog()
    
    # Alert
    dialog.alert(
        "Welcome",
        "Welcome to the application!",
        alert_type="success"
    )
    
    # Confirmation
    if dialog.confirm(
        "Delete Confirmation",
        "Are you sure you want to delete this item?",
        default=False
    ):
        console.print("[green]Item deleted[/green]")
    
    # Choice
    choice = dialog.choice(
        "Select Action",
        "What would you like to do?",
        choices=["View", "Edit", "Delete", "Cancel"]
    )
    console.print(f"Selected: {choice}")
    
    # Input
    name = dialog.input(
        "User Input",
        "Please enter your name:",
        default="User"
    )
    console.print(f"Hello, {name}!")
```

---

## Screen Layouts

### Full-Screen Application Template
```python
# app/ui/layouts/base.py
"""
Base layout for full-screen applications.
"""

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from datetime import datetime


class BaseLayout:
    """Base layout with header, body, and footer."""
    
    def __init__(self, title: str, console: Optional[Console] = None):
        self.title = title
        self.console = console or Console()
        self.layout = Layout()
        
        # Setup layout structure
        self.layout.split(
            Layout(name="header", size=3),