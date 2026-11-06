
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def pause():
    """Wait for the user before returning to the menu."""

    input("\nPress Enter to continue...")


def display_profile_settings(config, save_config):
    """Display and update the ANTON username."""

    console.print(
        "\n[bold cyan]PROFILE SETTINGS[/bold cyan]\n"
    )

    current_username = config.get("username", "User")

    console.print(
        f"Current username: [bold]{current_username}[/bold]\n"
    )

    choice = questionary.select(
        "What would you like to do?",
        choices=[
            "Change Username",
            "Back"
        ],
        qmark=""
    ).ask()

    if choice is None or choice == "Back":
        return

    if choice == "Change Username":

        new_username = questionary.text(
            "Enter your new username:",
            default=current_username,
            qmark=""
        ).ask()

        if new_username is None:
            return

        new_username = new_username.strip()

        if not new_username:
            console.print(
                "[red]Username cannot be empty.[/red]"
            )
            pause()
            return

        config["username"] = new_username

        save_config(config)

        console.print(
            "\n[green]Username updated successfully.[/green]"
        )

        pause()


def display_connection_status(config):
    """Display AI and Git connection information."""

    console.print(
        "\n[bold cyan]CONNECTION STATUS[/bold cyan]\n"
    )

    table = Table(
        title="ANTON Configuration",
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Setting")
    table.add_column("Current Value")

    # AI configuration
    provider = config.get("ai_provider")
    model = config.get("ai_model")

    if provider and model:
        ai_status = "Configured"
        ai_details = f"{provider} / {model}"
    else:
        ai_status = "Not configured"
        ai_details = "No AI model selected"

    table.add_row("AI Status", ai_status)
    table.add_row("AI Configuration", ai_details)

    # Git configuration
    repository = config.get("git_repository")
    local_path = config.get("git_local_path")

    if local_path:
        git_status = "Repository connected"
        git_details = str(local_path)
    elif repository:
        git_status = "Account configured"
        git_details = str(repository)
    else:
        git_status = "Not connected"
        git_details = "No repository selected"

    table.add_row("Git Status", git_status)
    table.add_row("Git Repository", git_details)

    # Profile
    table.add_row(
        "Username",
        config.get("username", "Not set")
    )

    # Workspace
    workspace_path = config.get("workspace_path")

    if workspace_path:
        workspace_details = str(workspace_path)
    else:
        workspace_details = "Not configured"

    table.add_row("Workspace", workspace_details)

    console.print(table)

    console.print(
        "\n[dim]API keys and credentials are not displayed.[/dim]"
    )

    pause()


def display_help():
    """Display instructions for using ANTON."""

    console.print(
        Panel(
            "[bold cyan]WELCOME TO ANTON HELP[/bold cyan]\n\n"
            "ANTON is an AI-powered repository analysis "
            "and documentation assistant.\n\n"
            "[bold]1. Analyze Project[/bold]\n"
            "Inspect a connected repository, its structure, "
            "programming languages, and Git status.\n\n"
            "[bold]2. Configure AI[/bold]\n"
            "Connect an AI provider such as Gemini, OpenAI, "
            "Anthropic, or local Ollama.\n\n"
            "[bold]3. Connect Git Repository[/bold]\n"
            "Connect a GitHub repository or select a local "
            "Git repository.\n\n"
            "[bold]4. Documentation[/bold]\n"
            "Generate README and architecture documentation "
            "using your configured AI provider.\n\n"
            "[bold]5. Settings & Help[/bold]\n"
            "Manage your profile, view configuration, "
            "and access help.",
            title="ANTON User Guide",
            border_style="cyan"
        )
    )

    console.print(
        "\n[bold]COMMON TROUBLESHOOTING[/bold]\n"
    )

    console.print(
        "[yellow]AI connection problems[/yellow]\n"
        "- Check your internet connection.\n"
        "- Verify your API key and selected model.\n"
        "- Check that your provider supports the model.\n"
    )

    console.print(
        "[yellow]Git connection problems[/yellow]\n"
        "- Check that Git is installed.\n"
        "- Verify your GitHub authentication.\n"
        "- Make sure the repository exists and is accessible.\n"
    )

    console.print(
        "[yellow]Python dependency problems[/yellow]\n"
        "- Navigate to the Anton directory.\n"
        "- Activate the virtual environment.\n"
        "- Install dependencies if a module is missing.\n"
    )

    console.print(
        "[dim]Run ANTON using: python3 main.py[/dim]"
    )

    pause()


def display_about():
    """Display information about ANTON."""

    console.print(
        Panel(
            "[bold cyan]ANTON[/bold cyan]\n\n"
            "AI-powered repository intelligence assistant.\n\n"
            "Purpose:\n"
            "Understand codebases, generate documentation, "
            "and assist with software engineering tasks.\n\n"
            "Current capabilities:\n"
            "- Repository analysis\n"
            "- AI provider integration\n"
            "- GitHub and local Git integration\n"
            "- AI-powered README generation\n"
            "- Architecture documentation generation\n\n"
            "Built with Python.",
            title="About ANTON",
            border_style="cyan"
        )
    )

    pause()


def settings_help_menu(config, save_config):
    """Main Settings & Help menu."""

    while True:

        console.print(
            "\n[bold cyan]SETTINGS & HELP[/bold cyan]\n"
        )

        choice = questionary.select(
            "Select an option:",
            choices=[
                "Profile Settings",
                "Connection Status",
                "Help & Troubleshooting",
                "About ANTON",
                "Back"
            ],
            qmark=""
        ).ask()

        if choice is None or choice == "Back":
            break

        elif choice == "Profile Settings":
            display_profile_settings(
                config,
                save_config
            )

        elif choice == "Connection Status":
            display_connection_status(config)

        elif choice == "Help & Troubleshooting":
            display_help()

        elif choice == "About ANTON":
            display_about()

