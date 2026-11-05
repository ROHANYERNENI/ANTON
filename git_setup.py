
import json
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

import questionary
import keyring

from rich.console import Console


console = Console()

# -----------------------------------------
# ANTON CONFIGURATION
# -----------------------------------------

WORKSPACE_DIR = Path.home() / "Anton" / "workspace"

KEYRING_SERVICE = "anton-git"
KEYRING_USERNAME = "github.com"


# -----------------------------------------
# COMMAND HELPERS
# -----------------------------------------

def run_command(command, env=None):

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            check=False
        )

        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

    except FileNotFoundError:
        return False, "", f"Command not found: {command[0]}"

    except Exception as error:
        return False, "", str(error)


def gh_available():

    success, _, _ = run_command(["gh", "--version"])

    return success


# -----------------------------------------
# GITHUB API
# -----------------------------------------

def github_request(endpoint, token):

    url = f"https://api.github.com/{endpoint.lstrip('/')}"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


# -----------------------------------------
# AUTHENTICATION
# -----------------------------------------

def authenticate_github():

    console.print("\n[bold]GITHUB AUTHENTICATION[/bold]")

    method = questionary.select(
        "How would you like to authenticate?",
        choices=[
            "GitHub CLI (Recommended)",
            "Personal Access Token",
            "Back"
        ],
        qmark=""
    ).ask()

    if method is None or method == "Back":
        return None

    token = None

    # GitHub CLI authentication

    if method == "GitHub CLI (Recommended)":

        if not gh_available():

            console.print(
                "\n[red]GitHub CLI is not installed.[/red]"
            )

            console.print("Install it using: brew install gh")

            return None

        console.print(
            "\n[dim]Starting GitHub authentication...[/dim]"
        )

        result = subprocess.run(
            [
                "gh",
                "auth",
                "login",
                "--hostname",
                "github.com",
                "--web"
            ],
            check=False
        )

        if result.returncode != 0:
            console.print("\n[red]GitHub authentication failed.[/red]")
            return None

        success, token, error = run_command(
            ["gh", "auth", "token", "--hostname", "github.com"]
        )

        if not success:
            console.print(f"\n[red]{error}[/red]")
            return None

    # Personal Access Token authentication

    elif method == "Personal Access Token":

        token = questionary.password(
            "Enter your GitHub Personal Access Token:",
            qmark=""
        ).ask()

        if not token:
            return None

    # Verify account

    try:

        account = github_request("user", token)

        username = account["login"]

        keyring.set_password(
            KEYRING_SERVICE,
            KEYRING_USERNAME,
            token
        )

        console.print(
            f"\n[bold green]Authenticated as {username}.[/bold green]"
        )

        return {
            "token": token,
            "username": username
        }

    except urllib.error.HTTPError as error:

        console.print(
            f"\n[red]GitHub rejected authentication: HTTP {error.code}[/red]"
        )

    except Exception as error:

        console.print(
            f"\n[red]Authentication error: {error}[/red]"
        )

    return None


# -----------------------------------------
# GET SAVED CREDENTIALS
# -----------------------------------------

def get_github_token():

    return keyring.get_password(
        KEYRING_SERVICE,
        KEYRING_USERNAME
    )


# -----------------------------------------
# REPOSITORY DISCOVERY
# -----------------------------------------

def get_repositories(token):

    try:

        repositories = github_request(
            "user/repos?sort=updated&per_page=100"
            "&affiliation=owner,collaborator,organization_member",
            token
        )

        return repositories

    except Exception as error:

        console.print(
            f"\n[red]Could not retrieve repositories: {error}[/red]"
        )

        return []


# -----------------------------------------
# REPOSITORY DETAILS
# -----------------------------------------

def get_repository_details(repository, token):

    try:

        return github_request(
            f"repos/{repository}",
            token
        )

    except Exception as error:

        console.print(
            f"\n[red]Repository not found or inaccessible: {error}[/red]"
        )

        return None


# -----------------------------------------
# BRANCH SELECTION
# -----------------------------------------

def select_branch(repository, token, default_branch):

    try:

        branches = github_request(
            f"repos/{repository}/branches?per_page=100",
            token
        )

        branch_names = [
            branch["name"] for branch in branches
        ]

        if not branch_names:
            return default_branch

        choices = list(branch_names)

        if default_branch not in choices:
            choices.insert(0, default_branch)

        return questionary.select(
            "Select the branch ANTON should use:",
            choices=choices,
            default=default_branch,
            qmark=""
        ).ask()

    except Exception as error:

        console.print(
            f"\n[yellow]Could not retrieve branches: {error}[/yellow]"
        )

        return default_branch


# -----------------------------------------
# CLONE REPOSITORY
# -----------------------------------------

def clone_repository(repository, token):

    WORKSPACE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    repository_name = repository.split("/")[-1]

    destination = WORKSPACE_DIR / repository_name

    if destination.exists():

        console.print(
            "\n[yellow]A folder with this repository name already exists.[/yellow]"
        )

        return None

    console.print(
        "\n[dim]Cloning repository into ANTON workspace...[/dim]"
    )

    environment = os.environ.copy()
    environment["GH_TOKEN"] = token

    success, output, error = run_command(
        [
            "gh",
            "repo",
            "clone",
            repository,
            str(destination)
        ],
        env=environment
    )

    if not success:

        console.print(
            f"\n[red]Clone failed: {error}[/red]"
        )

        return None

    console.print(
        "\n[bold green]Repository cloned successfully.[/bold green]"
    )

    return str(destination)


# -----------------------------------------
# LOCAL REPOSITORY
# -----------------------------------------

def connect_local_repository():

    path = questionary.text(
        "Enter the path to your local Git repository:",
        qmark=""
    ).ask()

    if not path:
        return None

    repository_path = Path(path).expanduser().resolve()

    success, output, error = run_command(
        [
            "git",
            "-C",
            str(repository_path),
            "rev-parse",
            "--show-toplevel"
        ]
    )

    if not success:

        console.print(
            "\n[red]This directory is not a valid Git repository.[/red]"
        )

        return None

    root_path = Path(output).resolve()

    console.print(
        f"\n[green]Local repository verified: {root_path}[/green]"
    )

    return {
        "repository": root_path.name,
        "branch": get_local_branch(root_path),
        "path": str(root_path)
    }


def get_local_branch(repository_path):

    success, branch, _ = run_command(
        [
            "git",
            "-C",
            str(repository_path),
            "branch",
            "--show-current"
        ]
    )

    return branch if success else "Unknown"


# -----------------------------------------
# REPOSITORY CONNECTION
# -----------------------------------------

def connect_repository(config, token, username):

    console.print("\n[bold]CONNECT A PROJECT[/bold]")

    method = questionary.select(
        "How would you like to connect your project?",
        choices=[
            "Browse GitHub Repositories",
            "Enter Repository URL",
            "Select Local Repository",
            "Back"
        ],
        qmark=""
    ).ask()

    if method is None or method == "Back":
        return False

    # Browse repositories

    if method == "Browse GitHub Repositories":

        repositories = get_repositories(token)

        if not repositories:
            console.print("\n[yellow]No repositories found.[/yellow]")
            return False

        repository_names = [
            repo["full_name"] for repo in repositories
        ]

        selected = questionary.select(
            "Select a GitHub repository:",
            choices=repository_names + ["Back"],
            qmark=""
        ).ask()

        if not selected or selected == "Back":
            return False

        repository = selected

    # Enter repository URL

    elif method == "Enter Repository URL":

        url = questionary.text(
            "Enter your GitHub repository URL:",
            qmark=""
        ).ask()

        if not url:
            return False

        parsed = urlparse(url)

        if parsed.scheme != "https" or parsed.hostname != "github.com":
            console.print("\n[red]Invalid GitHub repository URL.[/red]")
            return False

        parts = [
            part for part in parsed.path.strip("/").split("/")
            if part
        ]

        if len(parts) != 2:
            console.print("\n[red]Expected a URL like https://github.com/owner/repo[/red]")
            return False

        repository = f"{parts[0]}/{parts[1].removesuffix('.git')}"

    # Local repository

    elif method == "Select Local Repository":

        local = connect_local_repository()

        if not local:
            return False

        config["git_provider"] = "local"
        config["git_repository"] = local["repository"]
        config["git_branch"] = local["branch"]
        config["git_local_path"] = local["path"]
        config["git_connected"] = True

        return True

    # Verify remote repository

    details = get_repository_details(repository, token)

    if not details:
        return False

    default_branch = details.get("default_branch", "main")

    console.print(
        f"\n[green]Repository verified: {repository}[/green]"
    )

    branch = select_branch(
        repository,
        token,
        default_branch
    )

    if not branch:
        return False

    # Clone repository

    if not gh_available():

        console.print(
            "\n[red]GitHub CLI is required to clone repositories.[/red]"
        )

        return False

    local_path = clone_repository(repository, token)

    if not local_path:
        return False

    # Checkout selected branch

    success, _, error = run_command(
        [
            "git",
            "-C",
            local_path,
            "checkout",
            branch
        ]
    )

    if not success:
        console.print(
            f"\n[yellow]Could not switch branch: {error}[/yellow]"
        )
        return False

    # Save connection

    config["git_provider"] = "github"
    config["git_account"] = username
    config["git_repository"] = repository
    config["git_branch"] = branch
    config["git_local_path"] = local_path
    config["git_connected"] = True

    return True


# -----------------------------------------
# CONNECT GIT ACCOUNT
# -----------------------------------------

def connect_git_account(config):

    account = authenticate_github()

    if not account:
        return False

    return connect_repository(
        config,
        account["token"],
        account["username"]
    )


# -----------------------------------------
# TEST CURRENT CONNECTION
# -----------------------------------------

def test_git_connection(config):

    provider = config.get("git_provider")
    local_path = config.get("git_local_path")

    if provider == "local":

        success, output, error = run_command(
            ["git", "-C", local_path, "status", "--short", "--branch"]
        )

    else:

        token = get_github_token()

        if not token:
            console.print("\n[red]GitHub credentials not found.[/red]")
            return False

        try:

            details = github_request(
                f"repos/{config['git_repository']}",
                token
            )

            success = bool(details)

            error = "Repository inaccessible."

        except Exception as exception:

            success = False
            error = str(exception)

    if success:

        console.print(
            "\n[bold green]Git connection verified.[/bold green]"
        )

    else:

        console.print(
            f"\n[bold red]Connection failed: {error}[/bold red]"
        )

    return success


# -----------------------------------------
# MANAGE CURRENT CONNECTION
# -----------------------------------------

def manage_current_git(config):

    while True:

        console.print("\n[bold]CURRENT GIT CONNECTION[/bold]")

        console.print(
            f"Provider: {config.get('git_provider', 'Unknown')}"
        )

        console.print(
            f"Account: {config.get('git_account', 'Local repository')}"
        )

        console.print(
            f"Repository: {config.get('git_repository', 'Unknown')}"
        )

        console.print(
            f"Branch: {config.get('git_branch', 'Unknown')}"
        )

        console.print(
            f"Location: {config.get('git_local_path', 'Unknown')}"
        )

        choice = questionary.select(
            "Manage your Git connection:",
            choices=[
                "Test Connection",
                "Change Repository",
                "Disconnect Repository",
                "Disconnect Git Account",
                "Back"
            ],
            qmark=""
        ).ask()

        if choice is None or choice == "Back":
            return False

        elif choice == "Test Connection":

            test_git_connection(config)

        elif choice == "Change Repository":

            token = get_github_token()

            if config.get("git_provider") == "local":
                console.print(
                    "\n[yellow]Reconnect a local repository from the main Git menu.[/yellow]"
                )
                continue

            if not token:
                console.print("\n[red]GitHub credentials missing.[/red]")
                continue

            changed = connect_repository(
                config,
                token,
                config.get("git_account", "")
            )

            if changed:
                return True

        elif choice == "Disconnect Repository":

            confirmed = questionary.confirm(
                "Disconnect this repository? Local files will be preserved.",
                default=False,
                qmark=""
            ).ask()

            if confirmed:

                for key in [
                    "git_provider",
                    "git_repository",
                    "git_branch",
                    "git_local_path",
                    "git_connected"
                ]:
                    config.pop(key, None)

                return True

        elif choice == "Disconnect Git Account":

            confirmed = questionary.confirm(
                "Disconnect your GitHub account from ANTON?",
                default=False,
                qmark=""
            ).ask()

            if confirmed:

                if config.get("git_provider") == "github":

                    try:
                        keyring.delete_password(
                            KEYRING_SERVICE,
                            KEYRING_USERNAME
                        )

                    except keyring.errors.PasswordDeleteError:
                        pass

                    except Exception as error:
                        console.print(
                            f"\n[red]Could not remove credentials: {error}[/red]"
                        )
                        continue

                for key in [
                    "git_provider",
                    "git_account",
                    "git_repository",
                    "git_branch",
                    "git_local_path",
                    "git_connected"
                ]:
                    config.pop(key, None)

                return True


# -----------------------------------------
# MAIN GIT CONFIGURATION MENU
# -----------------------------------------

def git_configuration_menu(config):

    while True:

        console.print("\n[bold white]ANTON GIT MANAGEMENT[/bold white]")

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Manage Current Connection",
                "Connect Git Account",
                "Back"
            ],
            qmark=""
        ).ask()

        if choice is None or choice == "Back":
            return False

        elif choice == "Manage Current Connection":

            if not config.get("git_connected"):
                console.print(
                    "\n[yellow]No Git connection is configured.[/yellow]"
                )
                continue

            changed = manage_current_git(config)

            if changed:
                return True

        elif choice == "Connect Git Account":

            success = connect_git_account(config)

            if success:
                return True
