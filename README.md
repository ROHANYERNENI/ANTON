# Anton - Local Code AI Agent 🤖

Anton is a privacy-first, fully local AI agent that lives on your machine. It can read through any software codebase folder—either **locally from your hard drive** or **directly downloaded from the GitHub cloud**—memorize its architecture, and answer questions using the **DeepSeek-Coder 6.7B** model.

Because it runs completely locally via **Ollama**, no code data or private repository text is ever sent to external cloud servers or third parties.

---

## Prerequisites

Before running the agent, make sure your machine has the following tools installed:

1. **Python 3.10 or higher** (Python 3.12 is highly recommended).
2. **Ollama** (The local AI engine app).

---

## Setup Instructions

### Step 1: Install Ollama & Download DeepSeek-Coder

1. Download and install the free Ollama app from the official website: [ollama.com](https://ollama.com).
2. Open your system **Terminal** application and download the coding brain by running:
   ```bash
   ollama run deepseek-coder:6.7b
   ```
3. Once the download progress bar reaches 100%, type `/exit` and hit **Enter** to close the live chat.

### Step 2: Download this Project

Download or clone this repository to your computer and navigate your Terminal application inside the folder:

```bash
cd Anton
```

### Step 3: Configure Automatic Login (Optional but Recommended)

To prevent the agent from asking you for your GitHub Token and Username every time you boot it up, create a secret local lockbox file:

1. Create a file named `.env` right next to `agent.py`.
2. Paste your details inside exactly like this:
   ```text
   GITHUB_TOKEN=your_personal_access_token_here
   GITHUB_USERNAME=your_github_username_here
   ```
   _(Note: A classic GitHub personal access token with `repo` scope permissions is required to access private code repositories)._

### Step 4: Install Required Libraries

Install the necessary package frameworks by executing this command in your terminal:

```bash
python3.12 -m pip install -r requirements.txt --break-system-packages
```

### Step 5: Launch Anton

Start your personal code assistant:

```bash
python3.12 agent.py
```

---

## 💻 How to Use It

When you launch Anton, you will be presented with a menu configuration option:

### Option 1: Read a Local Folder

- Simply grab any code directory from your file manager (like Mac Finder), **drag and drop it directly into the terminal window** to auto-fill its pathway location, and hit Enter.

### Option 2: Link GitHub Repository

- If your `.env` configuration file is filled out, Anton will bypass the token entry fields seamlessly. Simply enter the name of the target repository you wish to scan (e.g., `ANTON-`) and hit Enter.

Once Anton displays: ` The agent has memorized the codebase!`, you can ask any engineering query you want:

- _"What does this overall project architecture look like?"_
- _"Can you review my code structure and find potential security flaws or performance bugs?"_
- _"Write a comprehensive suite of unit tests for the functions found inside my files."_

Type `exit` or `quit` at any time to close the terminal session.
