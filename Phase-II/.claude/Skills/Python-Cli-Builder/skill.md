# Python CLI Builder Agent - Professional Skill Profile

## Role Definition
**Python CLI Builder Agent** specialized in designing and building production-grade command-line applications with clear interfaces, robust error handling, and maintainable architecture.

---

## Core Responsibilities

### 1. CLI Design & Architecture
- Design intuitive command structures and subcommands
- Define clear argument and flag conventions
- Create consistent user interface patterns
- Plan command hierarchy and organization
- Document CLI behavior and usage
- Ensure backwards compatibility

### 2. Argument & Flag Management
- Implement positional arguments
- Define optional flags and switches
- Support short (`-f`) and long (`--flag`) formats
- Handle multiple values and lists
- Provide sensible defaults
- Validate input types and ranges

### 3. Input Validation & Error Handling
- Validate user input comprehensively
- Provide clear, actionable error messages
- Return appropriate exit codes (0-255)
- Handle edge cases gracefully
- Prevent invalid states
- Guide users toward correct usage

### 4. Code Structure & Modularity
- Separate CLI logic from business logic
- Create testable, reusable components
- Implement clean separation of concerns
- Follow single responsibility principle
- Enable easy extension and modification
- Maintain readable, documented code

### 5. Configuration Management
- Support environment variables
- Implement configuration file parsing (YAML, JSON, TOML, INI)
- Provide configuration precedence (CLI args > env vars > config file > defaults)
- Validate configuration schemas
- Support multiple configuration sources
- Enable configuration file generation

### 6. Logging & Output
- Implement structured logging
- Support multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Provide verbose and quiet modes
- Format output for human and machine consumption
- Support color-coded output (with disable option)
- Enable log file output

### 7. Help & Documentation
- Generate comprehensive help text
- Provide command examples
- Document all arguments and flags
- Create usage guides
- Support man pages (optional)
- Include version information

### 8. Cross-Platform Compatibility
- Work on Windows, macOS, and Linux
- Handle path separators correctly
- Manage line endings appropriately
- Support different terminal types
- Handle encoding issues
- Test on multiple platforms

### 9. Production Safety
- Implement proper signal handling (SIGINT, SIGTERM)
- Provide dry-run modes for destructive operations
- Confirm dangerous actions
- Handle resource cleanup
- Manage concurrent execution
- Prevent data corruption

---

## Technical Stack

### Core Libraries

#### Click (Recommended)
```python
import click

@click.command()
@click.option('--count', default=1, help='Number of iterations')
@click.option('--name', prompt='Your name', help='The person to greet')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f'Hello, {name}!')
```

**Strengths:**
- Decorator-based syntax
- Automatic help generation
- Built-in parameter validation
- Subcommand support
- Testing utilities
- Rich ecosystem

#### Argparse (Standard Library)
```python
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))
```

**Strengths:**
- No dependencies (stdlib)
- Well-documented
- Flexible
- Battle-tested

#### Typer (Modern Alternative)
```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str, count: int = 1):
    """Say hello to NAME COUNT times."""
    for _ in range(count):
        typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()
```

**Strengths:**
- Type hints for validation
- Automatic documentation
- Modern Python syntax
- Built on Click

### Supporting Libraries
```python
# Configuration Management
import yaml           # YAML config files
import tomli          # TOML config files
import configparser   # INI config files
from pydantic import BaseModel, ValidationError  # Config validation

# Logging
import logging
from rich.logging import RichHandler  # Beautiful logging
import structlog      # Structured logging

# Output Formatting
from rich.console import Console  # Rich text formatting
from rich.table import Table      # Tables
from rich.progress import track   # Progress bars
import tabulate      # Simple tables

# Environment Variables
from dotenv import load_dotenv   # .env file support
import os

# Path Handling
from pathlib import Path         # Cross-platform paths

# Testing
import pytest
from click.testing import CliRunner
```

---

## CLI Architecture Pattern

### Project Structure
```
my-cli-tool/
├── README.md
├── setup.py / pyproject.toml
├── requirements.txt
├── .env.example
├── my_cli/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── cli.py               # CLI interface
│   ├── commands/            # Command modules
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── build.py
│   │   └── deploy.py
│   ├── core/                # Business logic
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   └── deployer.py
│   ├── config.py            # Configuration management
│   ├── utils.py             # Utilities
│   └── exceptions.py        # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_commands.py
│   └── test_core.py
└── docs/
    ├── usage.md
    └── examples.md
```

### Entry Point Pattern
```python
# my_cli/__main__.py
"""Entry point for the CLI application."""

import sys
from my_cli.cli import main

if __name__ == '__main__':
    sys.exit(main())
```
```python
# setup.py or pyproject.toml
entry_points={
    'console_scripts': [
        'mycli=my_cli.cli:main',
    ],
}
```

---

## Complete CLI Implementation Template

### 1. Main CLI Interface (Click)
```python
# my_cli/cli.py
"""
Main CLI interface for MyTool.
"""

import sys
import click
from pathlib import Path
from typing import Optional

from my_cli import __version__
from my_cli.config import load_config, Config
from my_cli.exceptions import MyCliError
from my_cli.utils import setup_logging
from my_cli.commands import init, build, deploy


# Context object for sharing state
class Context:
    """CLI context object."""
    
    def __init__(self):
        self.config: Optional[Config] = None
        self.verbose: bool = False
        self.debug: bool = False


@click.group()
@click.version_option(version=__version__)
@click.option(
    '-c', '--config',
    type=click.Path(exists=True, path_type=Path),
    help='Path to configuration file',
    envvar='MYCLI_CONFIG'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug mode',
    envvar='MYCLI_DEBUG'
)
@click.pass_context
def main(ctx: click.Context, config: Optional[Path], verbose: bool, debug: bool):
    """
    MyTool - A production-grade CLI application.
    
    Use 'mycli COMMAND --help' for command-specific help.
    
    Examples:
    
      # Initialize a new project
      mycli init my-project
      
      # Build with custom config
      mycli -c config.yaml build
      
      # Deploy in verbose mode
      mycli -v deploy production
    """
    # Create context object
    ctx.obj = Context()
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug
    
    # Setup logging
    log_level = 'DEBUG' if debug else 'INFO' if verbose else 'WARNING'
    setup_logging(log_level)
    
    # Load configuration
    try:
        ctx.obj.config = load_config(config)
    except Exception as e:
        click.secho(f'Error loading configuration: {e}', fg='red', err=True)
        sys.exit(1)


# Register commands
main.add_command(init.init_command)
main.add_command(build.build_command)
main.add_command(deploy.deploy_command)


# Error handling wrapper
def safe_main():
    """Safe entry point with error handling."""
    try:
        main()
    except MyCliError as e:
        click.secho(f'Error: {e}', fg='red', err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.secho('\nOperation cancelled by user', fg='yellow', err=True)
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        click.secho(f'Unexpected error: {e}', fg='red', err=True)
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    safe_main()
```

### 2. Command Implementation
```python
# my_cli/commands/init.py
"""
Initialize command implementation.
"""

import click
from pathlib import Path
from typing import Optional

from my_cli.core.initializer import initialize_project
from my_cli.exceptions import ProjectExistsError


@click.command('init')
@click.argument('project_name')
@click.option(
    '-t', '--template',
    type=click.Choice(['basic', 'advanced', 'minimal']),
    default='basic',
    help='Project template to use'
)
@click.option(
    '-d', '--directory',
    type=click.Path(path_type=Path),
    default=None,
    help='Target directory (defaults to current directory)'
)
@click.option(
    '--force',
    is_flag=True,
    help='Overwrite existing project'
)
@click.pass_obj
def init_command(ctx, project_name: str, template: str, 
                 directory: Optional[Path], force: bool):
    """
    Initialize a new project.
    
    Creates a new project structure with the specified template.
    
    Examples:
    
      # Create basic project
      mycli init my-project
      
      # Create with advanced template
      mycli init my-project --template advanced
      
      # Create in specific directory
      mycli init my-project -d /path/to/projects
    """
    # Determine target directory
    target_dir = directory or Path.cwd()
    project_path = target_dir / project_name
    
    # Check if project exists
    if project_path.exists() and not force:
        click.secho(
            f'Project "{project_name}" already exists. Use --force to overwrite.',
            fg='red',
            err=True
        )
        raise click.Abort()
    
    # Confirm destructive operation
    if project_path.exists() and force:
        if not click.confirm(
            f'⚠️  This will overwrite existing project. Continue?',
            default=False
        ):
            raise click.Abort()
    
    # Initialize project with progress indication
    with click.progressbar(
        length=100,
        label='Initializing project'
    ) as bar:
        try:
            initialize_project(
                project_name=project_name,
                template=template,
                target_dir=target_dir,
                progress_callback=lambda p: bar.update(p)
            )
        except ProjectExistsError as e:
            click.secho(f'Error: {e}', fg='red', err=True)
            raise click.Abort()
    
    # Success message with next steps
    click.secho('✓ Project initialized successfully!', fg='green')
    click.echo()
    click.echo('Next steps:')
    click.echo(f'  cd {project_name}')
    click.echo('  mycli build')
    click.echo()
    click.echo(f'Project created at: {project_path}')
```

### 3. Configuration Management
```python
# my_cli/config.py
"""
Configuration management with validation.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, ValidationError


class BuildConfig(BaseModel):
    """Build configuration schema."""
    
    output_dir: Path = Field(default=Path('dist'))
    optimize: bool = Field(default=True)
    parallel: bool = Field(default=False)
    workers: int = Field(default=4, ge=1, le=32)


class DeployConfig(BaseModel):
    """Deploy configuration schema."""
    
    environment: str = Field(default='development')
    region: str = Field(default='us-east-1')
    auto_confirm: bool = Field(default=False)
    rollback_on_failure: bool = Field(default=True)


class Config(BaseModel):
    """Main configuration schema."""
    
    project_name: str = Field(default='my-project')
    version: str = Field(default='0.1.0')
    build: BuildConfig = Field(default_factory=BuildConfig)
    deploy: DeployConfig = Field(default_factory=DeployConfig)
    
    class Config:
        extra = 'forbid'  # Reject unknown fields


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file and environment variables.
    
    Precedence: CLI args > env vars > config file > defaults
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated configuration object
        
    Raises:
        ValidationError: If configuration is invalid
        FileNotFoundError: If config file doesn't exist
    """
    config_data: Dict[str, Any] = {}
    
    # 1. Load from config file
    if config_path:
        if not config_path.exists():
            raise FileNotFoundError(f'Config file not found: {config_path}')
        
        with open(config_path) as f:
            if config_path.suffix in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f) or {}
            elif config_path.suffix == '.json':
                import json
                config_data = json.load(f)
            else:
                raise ValueError(f'Unsupported config format: {config_path.suffix}')
    
    # 2. Override with environment variables
    if env_project := os.getenv('MYCLI_PROJECT_NAME'):
        config_data['project_name'] = env_project
    
    if env_env := os.getenv('MYCLI_ENVIRONMENT'):
        config_data.setdefault('deploy', {})['environment'] = env_env
    
    # 3. Validate and return
    try:
        return Config(**config_data)
    except ValidationError as e:
        raise ValueError(f'Invalid configuration: {e}')


def save_config(config: Config, output_path: Path):
    """Save configuration to file."""
    with open(output_path, 'w') as f:
        yaml.dump(config.dict(), f, default_flow_style=False)
```

### 4. Logging Setup
```python
# my_cli/utils.py
"""
Utility functions for CLI.
"""

import logging
import sys
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

console = Console()


def setup_logging(level: str = 'INFO', log_file: Optional[Path] = None):
    """
    Setup logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file to write logs to
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Setup handlers
    handlers = [
        RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True
        )
    ]
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        format='%(message)s'
    )
    
    # Suppress noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


logger = logging.getLogger(__name__)
```

### 5. Custom Exceptions
```python
# my_cli/exceptions.py
"""
Custom exceptions for CLI.
"""


class MyCliError(Exception):
    """Base exception for CLI errors."""
    
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


class ProjectExistsError(MyCliError):
    """Raised when project already exists."""
    
    def __init__(self, project_name: str):
        super().__init__(
            f'Project "{project_name}" already exists',
            exit_code=1
        )


class ConfigurationError(MyCliError):
    """Raised when configuration is invalid."""
    pass


class BuildError(MyCliError):
    """Raised when build fails."""
    
    def __init__(self, message: str):
        super().__init__(message, exit_code=2)


class DeploymentError(MyCliError):
    """Raised when deployment fails."""
    
    def __init__(self, message: str):
        super().__init__(message, exit_code=3)
```

### 6. Business Logic Separation
```python
# my_cli/core/builder.py
"""
Build logic - separate from CLI interface.
"""

import logging
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class Builder:
    """Handles project building."""
    
    def __init__(self, project_path: Path, config: dict):
        self.project_path = project_path
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'dist'))
    
    def build(self, progress_callback: Optional[Callable[[int], None]] = None):
        """
        Build the project.
        
        Args:
            progress_callback: Optional callback for progress updates (0-100)
            
        Raises:
            BuildError: If build fails
        """
        logger.info(f'Building project at {self.project_path}')
        
        steps = [
            ('Validating project structure', self._validate),
            ('Compiling sources', self._compile),
            ('Optimizing output', self._optimize),
            ('Generating artifacts', self._generate_artifacts),
        ]
        
        total_steps = len(steps)
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            logger.info(f'Step {i}/{total_steps}: {step_name}')
            
            try:
                step_func()
            except Exception as e:
                logger.error(f'Build failed at step: {step_name}')
                raise BuildError(f'Build failed: {e}')
            
            if progress_callback:
                progress = int((i / total_steps) * 100)
                progress_callback(progress)
        
        logger.info('Build completed successfully')
    
    def _validate(self):
        """Validate project structure."""
        required_files = ['package.json', 'src/main.py']
        
        for file in required_files:
            if not (self.project_path / file).exists():
                raise FileNotFoundError(f'Required file missing: {file}')
    
    def _compile(self):
        """Compile sources."""
        # Implementation here
        pass
    
    def _optimize(self):
        """Optimize output."""
        # Implementation here
        pass
    
    def _generate_artifacts(self):
        """Generate build artifacts."""
        # Implementation here
        pass
```

---

## Exit Codes Standard
```python
# Standard exit codes
EXIT_SUCCESS = 0           # Successful execution
EXIT_GENERAL_ERROR = 1     # General error
EXIT_MISUSE = 2           # Misuse of command
EXIT_CONFIG_ERROR = 3     # Configuration error
EXIT_NETWORK_ERROR = 4    # Network error
EXIT_PERMISSION_ERROR = 5 # Permission denied
EXIT_NOT_FOUND = 6        # Resource not found
EXIT_TIMEOUT = 7          # Operation timeout
EXIT_INTERRUPTED = 130    # Interrupted (Ctrl+C)
EXIT_TERMINATED = 143     # Terminated (SIGTERM)

# Usage in commands
def handle_error(error: Exception) -> int:
    """Map exceptions to exit codes."""
    if isinstance(error, FileNotFoundError):
        return EXIT_NOT_FOUND
    elif isinstance(error, PermissionError):
        return EXIT_PERMISSION_ERROR
    elif isinstance(error, ConfigurationError):
        return EXIT_CONFIG_ERROR
    elif isinstance(error, TimeoutError):
        return EXIT_TIMEOUT
    else:
        return EXIT_GENERAL_ERROR
```

---

## Input Validation Patterns

### Argument Validation
```python
import click
from pathlib import Path


def validate_email(ctx, param, value):
    """Validate email format."""
    import re
    if value and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
        raise click.BadParameter('Invalid email format')
    return value


def validate_port(ctx, param, value):
    """Validate port number."""
    if not 1 <= value <= 65535:
        raise click.BadParameter('Port must be between 1 and 65535')
    return value


@click.command()
@click.option('--email', callback=validate_email, help='User email')
@click.option('--port', type=int, callback=validate_port, help='Server port')
def configure(email, port):
    """Configure application."""
    pass
```

### Path Validation
```python
@click.command()
@click.argument(
    'input_file',
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path
    )
)
@click.argument(
    'output_dir',
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        path_type=Path
    )
)
def process(input_file: Path, output_dir: Path):
    """Process input file and write to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    # Processing logic
```

### Choice Validation
```python
@click.command()
@click.option(
    '--environment',
    type=click.Choice(['dev', 'staging', 'production'], case_sensitive=False),
    required=True,
    help='Deployment environment'
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=True),
    default='INFO',
    help='Logging level'
)
def deploy(environment, log_level):
    """Deploy application."""
    pass
```

### Range Validation
```python
@click.command()
@click.option(
    '--workers',
    type=click.IntRange(min=1, max=32),
    default=4,
    help='Number of worker processes'
)
@click.option(
    '--timeout',
    type=click.FloatRange(min=0.1, max=300.0),
    default=30.0,
    help='Timeout in seconds'
)
def run(workers, timeout):
    """Run application."""
    pass
```

---

## Testing Patterns

### CLI Testing with Click
```python
# tests/test_cli.py
"""
CLI tests using Click's testing utilities.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path

from my_cli.cli import main
from my_cli.commands.init import init_command


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def isolated_filesystem(runner):
    """Provide isolated filesystem for tests."""
    with runner.isolated_filesystem():
        yield Path.cwd()


def test_cli_version(runner):
    """Test version flag."""
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert 'version' in result.output.lower()


def test_cli_help(runner):
    """Test help output."""
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Usage:' in result.output
    assert 'Options:' in result.output


def test_init_command_success(runner, isolated_filesystem):
    """Test successful project initialization."""
    result = runner.invoke(init_command, ['test-project'])
    
    assert result.exit_code == 0
    assert 'successfully' in result.output.lower()
    assert (isolated_filesystem / 'test-project').exists()


def test_init_command_exists_error(runner, isolated_filesystem):
    """Test error when project already exists."""
    project_name = 'test-project'
    (isolated_filesystem / project_name).mkdir()
    
    result = runner.invoke(init_command, [project_name])
    
    assert result.exit_code != 0
    assert 'already exists' in result.output.lower()


def test_init_command_force_flag(runner, isolated_filesystem):
    """Test force flag overwrites existing project."""
    project_name = 'test-project'
    (isolated_filesystem / project_name).mkdir()
    
    result = runner.invoke(
        init_command,
        [project_name, '--force'],
        input='y\n'  # Confirm overwrite
    )
    
    assert result.exit_code == 0


def test_config_file_loading(runner, isolated_filesystem):
    """Test configuration file loading."""
    config_file = isolated_filesystem / 'config.yaml'
    config_file.write_text("""
project_name: test-project
build:
  optimize: true
  workers: 8
""")
    
    result = runner.invoke(main, ['-c', str(config_file), 'build'])
    assert result.exit_code == 0


def test_environment_variable_override(runner, monkeypatch):
    """Test environment variable configuration."""
    monkeypatch.setenv('MYCLI_DEBUG', '1')
    monkeypatch.setenv('MYCLI_PROJECT_NAME', 'env-project')
    
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0


def test_error_handling(runner):
    """Test error handling and exit codes."""
    result = runner.invoke(main, ['nonexistent-command'])
    
    assert result.exit_code != 0
    assert 'Error' in result.output or 'No such command' in result.output


@pytest.mark.parametrize('command,expected_exit', [
    (['--version'], 0),
    (['--help'], 0),
    (['init', '--help'], 0),
    (['invalid'], 2),
])
def test_exit_codes(runner, command, expected_exit):
    """Test various exit codes."""
    result = runner.invoke(main, command)
    assert result.exit_code == expected_exit
```

### Unit Testing Business Logic
```python
# tests/test_core.py
"""
Unit tests for business logic.
"""

import pytest
from pathlib import Path
from my_cli.core.builder import Builder
from my_cli.exceptions import BuildError


@pytest.fixture
def mock_project(tmp_path):
    """Create mock project structure."""
    project = tmp_path / 'test-project'
    project.mkdir()
    
    # Create required files
    (project / 'package.json').write_text('{}')
    (project / 'src').mkdir()
    (project / 'src' / 'main.py').write_text('print("hello")')
    
    return project


def test_builder_initialization(mock_project):
    """Test builder initialization."""
    config = {'output_dir': 'dist', 'optimize': True}
    builder = Builder(mock_project, config)
    
    assert builder.project_path == mock_project
    assert builder.config == config


def test_builder_validates_structure(tmp_path):
    """Test builder validates project structure."""
    invalid_project = tmp_path / 'invalid'
    invalid_project.mkdir()
    
    config = {}
    builder = Builder(invalid_project, config)
    
    with pytest.raises(BuildError):
        builder.build()


def test_builder_progress_callback(mock_project):
    """Test progress callback is called."""
    progress_updates = []
    
    def track_progress(value):
        progress_updates.append(value)
    
    config = {}
    builder = Builder(mock_project, config)
    builder.build(progress_callback=track_progress)
    
    assert len(progress_updates) > 0
    assert all(0 <= p <= 100 for p in progress_updates)
    assert progress_updates[-1] == 100
```

---

## Rich Output Examples

### Progress Bars
```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def deploy_with_progress(environment: str):
    """Deploy with rich progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        
        task = progress.add_task("[cyan]Deploying...", total=100)
        
        # Simulate deployment steps
        steps = [
            ("Building", 20),
            ("Testing", 40),
            ("Uploading", 70),
            ("Verifying", 100)
        ]
        
        for step_name, step_progress in steps:
            progress.update(task, description=f"[cyan]{step_name}...")
            # Do work here
            progress.update(task, completed=step_progress)
```

### Tables
```python
from rich.console import Console
from rich.table import Table

def display_status():
    """Display status as a table."""
    console = Console()
    
    table = Table(title="Deployment Status")
    table.add_column("Environment", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Version", style="green")
    
    table.add_row("Development", "✓ Active", "1.2.3")
    table.add_row("Staging", "✓ Active", "1.2.3")
    table.add_row("Production", "⚠ Deploying", "1.2.2")
    
    console.print(table)
```

### Panels and Syntax
```python
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

def display_config(config_text: str):
    """Display configuration with syntax highlighting."""
    console = Console()
    
    syntax = Syntax(config_text, "yaml", theme="monokai", line_numbers=