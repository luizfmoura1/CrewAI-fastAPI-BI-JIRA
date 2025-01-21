from utils.jira_client import JiraClient
from dotenv import load_dotenv
import os

# Carregando as variáveis de ambiente
load_dotenv()

# Configurações do Jira
BASE_URL = "https://ngosolucoes.atlassian.net"
EMAIL = "master@oppem.com.br"
API_TOKEN_JIRA = os.getenv("API_TOKEN_JIRA")
BOARD_ID = 24

# Criando o cliente do Jira
jira_client = JiraClient(base_url=BASE_URL, email=EMAIL, api_token=API_TOKEN_JIRA)

# Testando a requisição para buscar os dados do quadro
try:
    print("Fazendo requisição à API do Jira...")
    board_data = jira_client.get_single_board(board_id=BOARD_ID)
    print("Dados do Quadro:", board_data)
except Exception as e:
    print("Erro:", str(e))