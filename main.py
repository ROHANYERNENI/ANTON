
import ui
import json
from pathlib import Path
import questionary
from ai_setup import configure_ai
from ai_setup import ai_configuration_menu
from git_setup import git_configuration_menu
from analyze import analyze_project

def main():

    ui.display_banner()

    config = load_config()

    if not config.get("setup_complete"):
        if not first_time_setup(config):
            return

    username = config.get("username", "User")

    ui.display_welcome(username)

    while True:

        ui.display_status(
            ai_connected=bool(config.get("ai_provider")),
            git_connected=bool(config.get("git_repository"))
        )

        choice = ui.display_menu()

        if choice is None or choice == "Exit":

            ui.display_shutdown()
            break

        elif choice == "Analyze Project":
            analyze_project(config)

        elif choice == "Configure AI":

            changed = ai_configuration_menu(config)

            if changed:
                save_config(config)
                ui.display_success("AI settings updated.")

        elif choice == "Connect Git Repository":
            changed = git_configuration_menu(config)

            if changed:
                save_config(config)
                ui.display_success("Git configuration updated.")

        elif choice == "Documentation":

            ui.display_message(
                "Documentation is not implemented yet."
            )

        elif choice == "Settings & Help":

            ui.display_message(
                "Settings are not implemented yet."
            )


# Configuration paths

CONFIG_DIR = Path.home() / ".anton"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config():

    if not CONFIG_FILE.exists():
        return {}

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)

        return config if isinstance(config, dict) else {}

    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read ANTON configuration.")
        return {}


def save_config(config):

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


def first_time_setup(config):

    print("\nWelcome to ANTON.")
    print("Let's set up your workspace.\n")

    username = input("Enter your username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return False

    config["username"] = username
    config["setup_complete"] = True

    save_config(config)

    return True
if __name__ == "__main__":
    main()
