import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_config():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required.")
        
    return {
        "model": os.getenv("MODEL_NAME", "gpt-4-turbo"),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "seed": int(os.getenv("SEED", "42"))
    }
