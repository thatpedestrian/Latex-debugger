"""CLI interface for LaTeX Debugger using Click."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .core import LatexDebugger
from .utils import load_api_key, validate_api_key

console = Console()

HELP_TEXT = f"""[bold green]LaTeX Debugger[/bold green] v{__version__}

[bold]DESCRIPTION[/bold]
  LaTeX Debugger uses Gemini 3.5 Flash to fix syntax errors,
  indentation, spacing, and common warnings in your LaTeX files
  without changing the document's content or meaning.

[bold]QUICK START[/bold]
  1. Set your API key:  [cyan]set GEMINI_API_KEY=your_key[/cyan]
  2. Navigate to your project:  [cyan]cd my-latex-project[/cyan]
  3. Run the debugger:  [cyan]latex-debug[/cyan]

[bold]AVAILABLE COMMANDS[/bold]
  [green]latex-debug[/green]          Fix all .tex files in current directory
  [green]latex-debug fix[/green]      Fix a specific file or directory
  [green]latex-debug help-me[/green]  Show this help message
  [green]latex-debug version[/green]  Show version information
  [green]latex-debug init[/green]     Create a .env file template

[bold]FLAGS[/bold]
  [yellow]--dry-run[/yellow]          Preview changes without modifying files
  [yellow]--verbose[/yellow]          Show detailed output
  [yellow]--indent N[/yellow]         Set indentation size (default: 2)
  [yellow]--pattern GLOB[/yellow]     File pattern to match (e.g., "*.tex")
  [yellow]--api-key KEY[/yellow]      Specify API key directly
  [yellow]--restore[/yellow]          Restore file from .bak backup
  [yellow]--no-interactive[/yellow]   Skip file selection, fix all files

[bold]EXAMPLES[/bold]
  [dim]# Fix all .tex files in current directory[/dim]
  latex-debug

  [dim]# Preview changes without applying[/dim]
  latex-debug --dry-run

  [dim]# Fix specific file with verbose output[/dim]
  latex-debug fix paper.tex --verbose

  [dim]# Fix files matching a pattern[/dim]
  latex-debug --pattern "chapter*.tex"

  [dim]# Restore original from backup[/dim]
  latex-debug --restore paper.tex

[bold]CONFIGURATION[/bold]
  Create a [cyan].env[/cyan] file in your project directory:
  [dim]
  GEMINI_API_KEY=your_api_key_here
  [/dim]

  Get your API key at: https://aistudio.google.com/apikey

[bold]TROUBLESHOOTING[/bold]
  - "No API key" error: Set GEMINI_API_KEY in .env or environment
  - "Rate limit" error: Wait a moment and try again
  - "File not found": Check the file path and try again
"""


@click.group(invoke_without_command=True)
@click.option("--dry-run", is_flag=True, help="Preview changes without modifying files")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
@click.option("--indent", default=2, type=int, help="Indentation size (default: 2)")
@click.option("--pattern", default=None, help="File pattern to match (e.g., '*.tex')")
@click.option("--api-key", default=None, help="Gemini API key")
@click.option("--restore", "restore_file", default=None, help="Restore file from backup")
@click.option("--no-interactive", is_flag=True, help="Skip file selection, fix all files")
@click.version_option(__version__, "--version", "-V")
@click.pass_context
def cli(ctx, dry_run, verbose, indent, pattern, api_key, restore_file, no_interactive):
    """LaTeX Debugger - AI-powered LaTeX file fixer using Gemini 3.5 Flash.

    Fix syntax errors, indentation, and formatting in your LaTeX files
    without changing the document's content.
    """
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["verbose"] = verbose
    ctx.obj["indent"] = indent
    ctx.obj["pattern"] = pattern
    ctx.obj["no_interactive"] = no_interactive

    # Handle restore command
    if restore_file:
        _restore_file(restore_file)
        return

    # If no command invoked, show help or run default fix
    if ctx.invoked_subcommand is None:
        if not api_key and not load_api_key():
            console.print("[red]Error: No API key found![/red]")
            console.print("Run [cyan]latex-debug init[/cyan] to create a .env file template.")
            sys.exit(1)

        _run_fix(ctx, api_key)


def _restore_file(file_path: str):
    """Restore a file from its backup."""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        sys.exit(1)

    backup_path = path.with_suffix(path.suffix + ".bak")
    if not backup_path.exists():
        console.print(f"[red]Error: No backup found for {file_path}[/red]")
        console.print(f"Expected backup at: {backup_path}")
        sys.exit(1)

    import shutil
    shutil.copy2(backup_path, path)
    console.print(f"[green]Restored {file_path} from backup[/green]")


def _run_fix(ctx, api_key=None):
    """Run the fix command."""
    console.print("[bold green]LaTeX Debugger[/bold green]\n")

    # Load API key
    if not api_key:
        api_key = load_api_key()

    if not validate_api_key(api_key):
        console.print("[red]Error: Invalid or missing API key![/red]")
        console.print("Run [cyan]latex-debug init[/cyan] to create a .env file template.")
        sys.exit(1)

    # Initialize debugger
    debugger = LatexDebugger(
        api_key=api_key,
        indent_size=ctx.obj["indent"],
        dry_run=ctx.obj["dry_run"],
        verbose=ctx.obj["verbose"],
    )

    # Run fix
    results = debugger.fix_directory(
        pattern=ctx.obj["pattern"],
        interactive=not ctx.obj.get("no_interactive", False)
    )

    # Print summary
    debugger.print_summary()

    # Exit with appropriate code
    if not results["success"]:
        sys.exit(1)


@cli.command()
def init():
    """Create a .env file template for API key configuration."""
    env_path = Path(".env")

    if env_path.exists():
        console.print("[yellow].env file already exists![/yellow]")
        if not click.confirm("Overwrite existing .env file?"):
            return

    env_content = """# LaTeX Debugger Configuration
# Get your API key at: https://aistudio.google.com/apikey

GEMINI_API_KEY=your_api_key_here
"""

    env_path.write_text(env_content)
    console.print("[green]Created .env file template[/green]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Open .env file")
    console.print("2. Replace 'your_api_key_here' with your actual API key")
    console.print("3. Save the file")


@cli.command()
def version():
    """Show version information."""
    console.print(f"\n[bold]LaTeX Debugger[/bold] v{__version__}")
    console.print("AI-powered LaTeX file fixer using Gemini 3.5 Flash\n")


@cli.command()
@click.argument("file_path")
def fix(file_path):
    """Fix a specific LaTeX file.

    FILE_PATH is the path to the .tex file to fix.
    """
    from .core import Spinner
    
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        sys.exit(1)

    api_key = load_api_key()
    if not validate_api_key(api_key):
        console.print("[red]Error: No valid API key found![/red]")
        sys.exit(1)

    debugger = LatexDebugger(
        api_key=api_key,
        dry_run=click.get_current_context().obj.get("dry_run", False),
        verbose=click.get_current_context().obj.get("verbose", False),
    )

    spinner = Spinner(f"Fixing {path.name}")
    spinner.start()
    success, message = debugger.fix_file(path)
    spinner.stop(f"Done fixing {path.name}")
    console.print(f"  {message}")


@cli.command()
def help_me():
    """Show detailed help with examples and usage information."""
    console.print(HELP_TEXT, highlight=False)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
