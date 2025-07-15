# src/config/config.py

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Jira
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
API_TOKEN_JIRA = os.getenv("API_TOKEN_JIRA")

# Databricks Model Serving
# --- MUDANÇA AQUI ---
# Removemos o final "/invocations" da URL
DATABRICKS_ENDPOINT = os.getenv("DATABRICKS_ENDPOINT")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")