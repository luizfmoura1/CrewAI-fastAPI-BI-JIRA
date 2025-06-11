import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Jira
BASE_URL        = os.getenv("BASE_URL")
EMAIL           = os.getenv("EMAIL")
API_TOKEN_JIRA  = os.getenv("API_TOKEN_JIRA")

# OpenAI
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
