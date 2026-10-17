import os
import ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.github import GithubRepositoryReader

# 1. Make sure the local brain is ready
print("Checking local AI engine status...")
ollama.pull("deepseek-coder:6.7b")

Settings.llm = Ollama(model="deepseek-coder:6.7b", request_timeout=90.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

print("\n--- Anton AI Agent Menu ---")
print("1. Read a Local Folder")
print("2. Link GitHub Repository via Token")
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
    print("\n💡 To link GitHub, you need a Personal Access Token.")
    print("Create one here: https://github.com")
    
    token = input("\nPaste your GitHub Access Token: ").strip()
    owner = input("Enter the GitHub Username/Owner of the repo: ").strip()
    repo = input("Enter the Repository Name: ").strip()
    branch = input("Enter the Branch Name (default is 'main'): ").strip() or "main"
    
    # Save the token to environment memory so the tool can grab it implicitly
    os.environ["GITHUB_TOKEN"] = token
    
    print(f"\nConnecting to GitHub and fetching '{owner}/{repo}'...")
    try:
        reader = GithubRepositoryReader(
            github_client=None, 
            owner=owner,
            repo=repo,
            use_parser=False,
            verbose=False,
        )
        documents = reader.load_data(branch=branch)
    except Exception as e:
        print(f"\n❌ Failed to fetch repository. Error: {e}")
        exit()

else:
    print("Invalid choice. Exiting.")
    exit()

# 3. Create the database index from whatever data was loaded
print("\nIndexing codebase... Please wait a moment...")
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
