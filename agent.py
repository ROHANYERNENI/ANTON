import os
import ollama
from github import Github
from dotenv import load_dotenv, set_key  # Added set_key to write values dynamically
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Path to our local background memory configuration file
ENV_FILE_PATH = ".env"

# Create a blank memory file if it doesn't exist yet
if not os.path.exists(ENV_FILE_PATH):
    with open(ENV_FILE_PATH, "w") as f:
        pass

# 1. Load the existing secrets from the background file
load_dotenv(dotenv_path=ENV_FILE_PATH)

print("Checking local AI engine status...")
ollama.pull("deepseek-coder:6.7b")

Settings.llm = Ollama(model="deepseek-coder:6.7b", request_timeout=90.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

print("\n--- Anton AI Agent Menu ---")
print("1. Read a Local Folder")
print("2. Link GitHub Repository")
choice = input("Choose an option (1 or 2): ").strip()

documents = []

if choice == "1":
    repo_path = input("\nPaste the path to your local code folder: ").strip()
    repo_path = repo_path.replace("'", "").replace('"', "")
    if not os.path.exists(repo_path):
        print("Oops! That folder doesn't exist.")
        exit()
    print("\nReading your local files...")
    documents = SimpleDirectoryReader(repo_path, recursive=True).load_data()

elif choice == "2":
    # Check background memory configurations
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_USERNAME")
    repo_name = os.getenv("GITHUB_REPO")
    
    # --- SMART INITIAL SETUP INTERFACE ---
    # If the token is missing, ask the user and write it down for next time
    if not token:
        token = input("\n🔑 Paste your GitHub Access Token (First-time setup): ").strip()
        set_key(ENV_FILE_PATH, "GITHUB_TOKEN", token)
        print("💾 Token saved to configuration configuration successfully!")
    else:
        print("\n🔑 GitHub Access Token loaded automatically from memory.")
        
    # If the username is missing, ask the user and write it down for next time
    if not owner:
        owner = input("👤 Enter your GitHub Username/Owner: ").strip()
        set_key(ENV_FILE_PATH, "GITHUB_USERNAME", owner)
        print("💾 Username saved to configuration configuration successfully!")
    else:
        print(f"👤 Repository Owner loaded automatically: {owner}")
        
    # If the target repository name is missing, ask the user and write it down
    if not repo_name:
        repo_name = input("📦 Enter the Repository Name: ").strip()
        set_key(ENV_FILE_PATH, "GITHUB_REPO", repo_name)
        print("💾 Repository name saved to configuration configuration successfully!")
    else:
        print(f"📦 Repository Name loaded automatically: {repo_name}")
        
    branch = input("Enter the Branch Name (default is 'main'): ").strip() or "main"
    
    print(f"\nConnecting to GitHub and fetching '{owner}/{repo_name}'...")
    try:
        from github import Auth
        auth = Auth.Token(token)
        g = Github(auth=auth)
        
        repo = g.get_repo(f"{owner}/{repo_name}")
        contents = repo.get_contents("", ref=branch)
        print("Downloading code files from the cloud...")
        
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path, ref=branch))
            else:
                if any(file_content.name.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.zip', '.tar', '.gz', '.pdf', '.ico']):
                    continue
                try:
                    decoded = file_content.decoded_content.decode('utf-8')
                    documents.append(Document(text=decoded, metadata={"file_name": file_content.name, "file_path": file_content.path}))
                except:
                    continue
                    
        if not documents:
            print("❌ Found no readable text/code files in the repository.")
            exit()
            
    except Exception as e:
        print(f"\n❌ Failed to fetch repository. Error: {e}")
        print("💡 Hint: If your token expired, open the '.env' file on your Mac and update it.")
        exit()

else:
    print("Invalid choice. Exiting.")
    exit()

print(f"\nIndexing {len(documents)} code elements... Please wait a moment...")
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

print("\n🎉 The agent has memorized the codebase! Type 'exit' to stop.")

while True:
    user_question = input("\nYou: ")
    if user_question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    
    print("\nDeepSeek is thinking...")
    response = query_engine.query(user_question)
    print(f"\nAgent:\n{response}")
