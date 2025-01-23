from fastapi import FastAPI, HTTPException
from src.utils.jira_client import JiraClient
from dotenv import load_dotenv
from src.main import main
import os
import logging

# Configurando o logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Carregando as variáveis de ambiente
load_dotenv()

# Configurações do Jira
BASE_URL = "https://ngosolucoes.atlassian.net"
EMAIL = "master@oppem.com.br"
API_TOKEN_JIRA = os.getenv("API_TOKEN_JIRA")  # Carregado do arquivo .env

# Verifique se o token foi carregado corretamente
if not API_TOKEN_JIRA:
    logger.error("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")
    raise ValueError("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")

# Inicializando a aplicação FastAPI
app = FastAPI()

# Criando o cliente do Jira
jira_client = JiraClient(base_url=BASE_URL, email=EMAIL, api_token=API_TOKEN_JIRA)

# Novo endpoint para buscar dados do quadro
@app.get("/JIRA_analitycs")
def get_analitycs(board_id: str, sprint_id: str) -> dict:
    try:
        # Buscando os dados do quadro e da sprint
        board_data = jira_client.get_single_board(board_id, sprint_id)
        response = main(board_data)
        final_content = {'data': [response]}
        return final_content
    except Exception as e:
        # Logando o erro completo
        logger.error(f"Erro ao buscar o quadro: {str(e)}", exc_info=True)
        # Retornando um erro 500 em caso de falha
        raise HTTPException(status_code=500, detail=str(e))
    
