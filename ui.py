
import questionary
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align


console = Console()

# ANTON BRANDING

def display_banner():

    banner = """
     █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ██╗
    ██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗  ██║
    ███████║██╔██╗ ██║   ██║   ██║   ██║██╔██╗ ██║
    ██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╗██║
    ██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝
    """

    console.print(
        
            Text(banner, style="bold white")
        
    )

# WELCOME SCREEN

def display_welcome(username):

    console.print()

    console.print(
        
        (f"[bold white]Hello!, {username}.[/bold white]\n")
    )



# SYSTEM STATUS


def display_status(ai_connected=False, git_connected=False):

    ai_status = (
        "[green]Connected[/green]"
        if ai_connected else
        "[red]Not connected[/red]"
    )

    git_status = (
        "[green]Connected[/green]"
        if git_connected else
        "[red]Not connected[/red]"
    )

    console.print("\n[bold]SYSTEM STATUS[/bold]")

    console.print(f"  AI       {ai_status}")
    console.print(f"  Git      {git_status}")

# MAIN NAVIGATION

def display_menu():

    choices = [
        "Analyze Project",
        "Configure AI",
        "Connect Git Repository",
        "Documentation",
        "Settings & Help",
        "Exit"
    ]

    return questionary.select(
        "What would you like to do?",
        choices=choices,
        instruction="Navigate using ↑ ↓ and press Enter",
        qmark=""
    ).ask()


# --------------------------------
# MESSAGES
# --------------------------------

def display_message(message):

    console.print(f"\n[dim]{message}[/dim]")


def display_error(message):

    console.print(f"\n[bold red]Error:[/bold red] {message}")


def display_success(message):

    console.print(f"\n[bold green]✓[/bold green] {message}")


def display_shutdown():

    console.print("\n[dim]ANTON shutting down.[/dim]")
