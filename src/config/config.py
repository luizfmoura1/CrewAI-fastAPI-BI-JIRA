import os
from dotenv import load_dotenv

load_dotenv()

# Jira
BASE_URL        = os.getenv("BASE_URL")
EMAIL           = os.getenv("EMAIL")
API_TOKEN_JIRA  = os.getenv("API_TOKEN_JIRA")

# OpenAI (ou outras)
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
