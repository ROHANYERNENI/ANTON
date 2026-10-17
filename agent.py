import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 1. Setup the DeepSeek Coder brain through Ollama
Settings.llm = Ollama(model="deepseek-coder:6.7b", request_timeout=60.0)

# 2. Setup a local embedding model to understand code structure
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

print("--- Local DeepSeek Code Agent ---")
repo_path = input("Paste the path to your code folder: ").strip()

# If the user drags and drops a folder, it might have trailing spaces or quotes, let's clean it up
repo_path = repo_path.replace("'", "").replace('"', "")

if not os.path.exists(repo_path):
    print(f"Oops! That folder doesn't exist at: {repo_path}")
    exit()

print("\nReading your codebase... Please wait a moment...")
# Load all the files inside your code folder
documents = SimpleDirectoryReader(repo_path, recursive=True).load_data()

# Build the temporary index database
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

print("\n🎉 The agent has memorized your code! Type 'exit' to stop.")

while True:
    user_question = input("\nYou: ")
    if user_question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    
    print("\nDeepSeek is thinking...")
    response = query_engine.query(user_question)
    print(f"\nAgent:\n{response}")

