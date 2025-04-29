"""
RAT: Retrieval Augmented Thoughts - Main Entry Point
"""
import os
from dotenv import load_dotenv
from src.ui import create_demo

# Load environment variables
load_dotenv()

# Check required environment variables
required_keys = ["NOMIC_API_KEY", "LLAMA_CLOUD_API_KEY"]
missing_keys = [key for key in required_keys if not os.environ.get(key)]
if missing_keys:
    print(f"Error: Missing required environment variables: {', '.join(missing_keys)}")
    print("Please create a .env file with the required API keys")
    exit(1)

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(server_name="0.0.0.0", debug=True)