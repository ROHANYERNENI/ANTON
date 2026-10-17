# Anton - Local Code AI Agent 🤖

Anton is a privacy-first, fully local AI agent that lives on your machine. It can read through any software codebase folder, memorize its architecture, and answer questions, find bugs, or explain code logic using the **DeepSeek-Coder 6.7B** model.

Because it runs completely locally on your machine via **Ollama**, no code data is ever sent to external cloud servers or third parties.

---

## Prerequisites

Before running the agent, make sure your machine has the following tools installed:

1. **Python 3.10 or higher** (Python 3.12 is highly recommended).
2. **Ollama** (The local AI engine).

---

## Setup Instructions

Follow these 4 simple steps to get Anton up and running on your computer.

### Step 1: Install Ollama & Download DeepSeek-Coder

1. Download and install the free Ollama app from the official website: [ollama.com](https://ollama.com).
2. Open your system **Terminal** application.
3. Download and start the coding model by running the following command:
   ```bash
   ollama run deepseek-coder:6.7b
   ```
4. Wait for the download progress bar to reach 100%. Once you see the `>>> Send a message` prompt, type `/exit` and hit **Enter** to close the live chat.

### Step 2: Download this Repository

Download this repository to your computer and open your Terminal application inside the project folder:

```bash
cd Anton
```

### Step 3: Install Required Python Libraries

Install the necessary AI framework pieces by executing this command in your terminal:

```bash
python3 -m pip install -r requirements.txt --break-system-packages
```

_(Note: The `--break-system-packages` flag is required on modern operating systems to allow custom user scripts to execute safely outside global system paths)._

### Step 4: Launch the Agent

Start your personal code assistant using the following command:

```bash
python3 agent.py
```

---

## How to Use It

1. When you run `python3 agent.py`, the agent will display:
   `Paste the path to your code folder:`
2. Open your normal file manager (like Mac Finder or Windows Explorer), grab any code folder you want to inspect, and **drag and drop it directly into the terminal window**. The terminal will automatically fill in the path!
3. Press **Enter**. The agent will display a loading confirmation status.
4. Once it successfully indexes your files, you will see a prompt to ask your questions!

### 💡 Example Questions to Try:

- _"What does this overall project architecture look like?"_
- _"Where is the main entry point or routing configuration file?"_
- _"Can you review my code structure and find potential logic bugs or optimization errors?"_
- _"Write a comprehensive suite of unit tests for the functions found inside this specific file."_

Type `exit` or `quit` at any time to close the terminal session.
# ANTON-
