import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get tokens from environment
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment variables")
if not NOTION_API_KEY:
    raise ValueError("NOTION_API_KEY not found in environment variables")

# Rest of your test code here...
