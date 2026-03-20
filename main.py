"""RAT: Retrieval Augmented Thoughts - Main Entry Point"""
import os
from dotenv import load_dotenv
from src.ui import create_demo

# Load API keys and config from .env
load_dotenv()

# Optional: Validate required environment variables
# required_keys = ["nk-p4RbLXYiBQInfAQyrlCssat_n9w-697uXrq4dlCmq0o", "llx-nxrF5SQ5MnbMrKhrb1HqfdFA3YajxTDjtjfctsyebDSdBa7W"]
# missing_keys = [key for key in required_keys if not os.environ.get(key)]
# if missing_keys:
#     print(f"Error: Missing required environment variables: {', '.join(missing_keys)}")
#     print("Please create a .env file with the required API keys")
#     exit(1)

if __name__ == "__main__":
    demo = create_demo()
    # Launch Gradio server accessible from any network interface
    demo.launch(server_name="0.0.0.0", debug=True)