import os
import ollama
from github import Github
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 1. Load the secrets from the hidden .env file
load_dotenv()

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
    saved_token = os.getenv("GITHUB_TOKEN")
    saved_username = os.getenv("GITHUB_USERNAME")
    
    if saved_token:
        token = saved_token
        print("\n🔑 GitHub Access Token loaded automatically.")
    else:
        token = input("\nPaste your GitHub Access Token: ").strip()
        
    if saved_username:
        owner = saved_username
        print(f"👤 Repository Owner loaded automatically: {owner}")
    else:
        owner = input("Enter the GitHub Username/Owner of the repo: ").strip()
        
    repo_name = input("Enter the Repository Name: ").strip()
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
