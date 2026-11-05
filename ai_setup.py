from curses import flash
import json
import urllib.request
import urllib.error
import urllib.parse

import questionary
import keyring

from rich.console import Console


console = Console()


# -----------------------------------------
# PROVIDER CONFIGURATION
# -----------------------------------------

PROVIDERS = {
    "Ollama (Local AI)": {
        "id": "ollama",
        "default_url": "http://localhost:11434"
    },

    "OpenAI": {
        "id": "openai",
        "default_url": "https://api.openai.com"
    },

    "Google Gemini": {
        "id": "gemini",
        "default_url": "https://generativelanguage.googleapis.com"
    },

    "Anthropic": {
        "id": "anthropic",
        "default_url": "https://api.anthropic.com"
    }
}


# -----------------------------------------
# HTTP REQUEST HELPER
# -----------------------------------------

def make_request(url, headers=None):

    request = urllib.request.Request(
        url,
        headers=headers or {},
        method="GET"
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


# -----------------------------------------
# PROVIDER CONNECTION TEST
# -----------------------------------------

def test_connection(provider, base_url, api_key=None):

    try:

        if provider == "ollama":

            response = make_request(
                f"{base_url}/api/tags"
            )

            models = response.get("models", [])

            return True, models

        elif provider == "openai":

            response = make_request(
                "https://api.openai.com/v1/models",
                {
                    "Authorization": f"Bearer {api_key}"
                }
            )

            return True, response.get("data", [])

        elif provider == "gemini":

            url = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models?"
                + urllib.parse.urlencode({"key": api_key})
            )

            response = make_request(url)

            return True, response.get("models", [])

        elif provider == "anthropic":

            response = make_request(
                "https://api.anthropic.com/v1/models",
                {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                }
            )       
            return True, response.get("data", [])
      
    except urllib.error.HTTPError as error:

        return False, f"HTTP {error.code}: {error.reason}"

    except urllib.error.URLError as error:

        return False, str(error.reason)

    except Exception as error:

        return False, str(error)

    return False, "Unsupported provider."


# -----------------------------------------
# MODEL SELECTION
# -----------------------------------------

def select_model(provider, models):

    if provider == "ollama":

        if not models:
            console.print(
                "\n[yellow]No local models found.[/yellow]"
            )
            console.print(
                "Install one using: ollama pull llama3.2"
            )
            return None

        model_names = [
            model["name"] for model in models
        ]

        return questionary.select(
            "Select your local model:",
            choices=model_names,
            qmark=""
        ).ask()

    defaults = {
        "openai": "gpt-4.1-mini",
        "gemini": "gemini-3.8-flash",
        "anthropic": "claude-sonnet-4-5"
    }

    return questionary.text(
        "Enter your model ID:",
        default=defaults.get(provider, ""),
        qmark=""
    ).ask()


# -----------------------------------------
# MAIN AI SETUP
# -----------------------------------------

def configure_ai(config):

    console.print("\n[bold white]ANTON AI CONFIGURATION[/bold white]")
    console.print("[dim]Connect your preferred AI provider.[/dim]\n")

    # STEP 1: Choose provider

    selected_provider = questionary.select(
        "Which AI provider would you like ANTON to use?",
        choices=list(PROVIDERS.keys()) +["Back"],
        qmark=""
    ).ask()

    if selected_provider is None or selected_provider == "Back":
        return False

    provider_info = PROVIDERS[selected_provider]

    provider = provider_info["id"]

    base_url = provider_info["default_url"]

    # STEP 2: Authentication

    api_key = None

    if provider == "ollama":

        base_url = questionary.text(
            "Enter your Ollama server address:",
            default=base_url,
            qmark=""
        ).ask()

        if not base_url:
            return False

        base_url = base_url.rstrip("/")

    else:

        api_key = questionary.password(
            f"Enter your {selected_provider} API key:",
            qmark=""
        ).ask()

        if not api_key:
            console.print("\n[red]API key cannot be empty.[/red]")
            return False

    # STEP 3: Verify connection

    console.print("\n[dim]Testing connection...[/dim]")

    connected, result = test_connection(
        provider,
        base_url,
        api_key
    )

    if not connected:

        console.print(
            f"\n[bold red]Connection failed:[/bold red] {result}"
        )

        return False

    console.print(
        "\n[bold green]Provider authentication successful.[/bold green]"
    )

    # STEP 4: Select model

    model = select_model(provider, result)

    if not model:
        return False

    # STEP 5: Save credentials securely

    if api_key:

        try:
            keyring.set_password(
                "anton",
                provider,
                api_key
            )

        except Exception as error:

            console.print(
                f"\n[red]Could not save API key: {error}[/red]"
            )

            return False

    # STEP 6: Save configuration

    config["ai_provider"] = provider
    config["ai_model"] = model
    config["ai_base_url"] = base_url
    config["ai_configured"] = True

    console.print("\n[bold green]AI configuration saved.[/bold green]")

    console.print(f"Provider: {provider}")
    console.print(f"Model: {model}")

    return True

# -----------------------------------------
# MANAGE CURRENT AI
# -----------------------------------------

def manage_current_ai(config):

    provider = config.get("ai_provider")
    model = config.get("ai_model")
    base_url = config.get("ai_base_url")

    if not provider:
        console.print("\n[yellow]No AI provider is configured.[/yellow]")
        return False

    console.print("\n[bold]CURRENT AI CONNECTION[/bold]")
    console.print(f"Provider: {provider}")
    console.print(f"Model: {model or 'Not specified'}")

    while True:

        choice = questionary.select(
            "Manage your current AI:",
            choices=[
                "Test Connection",
                "Delete Current AI",
                "Back"
            ],
            qmark=""
        ).ask()

        if choice is None or choice == "Back":
            return False

        elif choice == "Test Connection":

            api_key = None

            if provider != "ollama":
                api_key = keyring.get_password(
                    "anton",
                    provider
                )

            console.print("\n[dim]Testing connection...[/dim]")

            connected, result = test_connection(
                provider,
                base_url,
                api_key
            )

            if connected:
                console.print(
                    "\n[bold green]Connection successful.[/bold green]"
                )
            else:
                console.print(
                    f"\n[bold red]Connection failed: {result}[/bold red]"
                )

        elif choice == "Delete Current AI":

            confirmed = questionary.confirm(
                "Are you sure you want to delete this AI connection?",
                default=False,
                qmark=""
            ).ask()

            if not confirmed:
                continue

            # Delete saved API key from Keychain

            if provider != "ollama":

                try:
                    keyring.delete_password(
                        "anton",
                        provider
                    )

                except keyring.errors.PasswordDeleteError:
                    pass

                except Exception as error:
                    console.print(
                        f"\n[red]Could not delete API key: {error}[/red]"
                    )
                    continue

            # Remove AI configuration

            config.pop("ai_provider", None)
            config.pop("ai_model", None)
            config.pop("ai_base_url", None)
            config.pop("ai_configured", None)

            console.print(
                "\n[bold green]AI connection deleted successfully.[/bold green]"
            )

            return True


# -----------------------------------------
# AI CONFIGURATION MENU
# -----------------------------------------

def ai_configuration_menu(config):

    while True:

        console.print("\n[bold white]ANTON AI MANAGEMENT[/bold white]")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Manage Current AI",
                "Add New AI",
                "Back"
            ],
            qmark=""
        ).ask()

        if choice is None or choice == "Back":
            return False

        elif choice == "Manage Current AI":

            if not config.get("ai_provider"):
                console.print(
                    "\n[yellow]No AI is currently configured. "
                    "Select Add New AI to get started.[/yellow]"
                )
                continue

            changed = manage_current_ai(config)

            if changed:
                return True

        elif choice == "Add New AI":

            success = configure_ai(config)

            if success:
                return True
