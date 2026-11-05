from main import load_config
from ai_client import generate_text

config = load_config()

response = generate_text(
    config,
    "Explain what a Python function is in two sentences."
)

print("\nANTON AI RESPONSE:\n")
print(response)
