import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token from environment
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment variables")

# Rest of your code here...
