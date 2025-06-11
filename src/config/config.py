import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Jira
BASE_URL        = os.getenv("BASE_URL")
EMAIL           = os.getenv("EMAIL")
API_TOKEN_JIRA  = os.getenv("API_TOKEN_JIRA")


# Databricks Model Serving
DATABRICKS_ENDPOINT="https://adb-4450746371403902.2.azuredatabricks.net/serving-endpoints/TesteProvisioned/invocations"
DATABRICKS_TOKEN="seu_token_do_databricks_aqui"
