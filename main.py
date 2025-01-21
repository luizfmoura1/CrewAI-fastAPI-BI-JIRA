from fastapi import FastAPI, HTTPException
from utils.jira_client import JiraClient
from dotenv import load_dotenv
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
BOARD_ID = 24  # Usando o board_id fixo

# Verifique se o token foi carregado corretamente
if not API_TOKEN_JIRA:
    logger.error("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")
    raise ValueError("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")

# Inicializando a aplicação FastAPI
app = FastAPI()

# Criando o cliente do Jira
jira_client = JiraClient(base_url=BASE_URL, email=EMAIL, api_token=API_TOKEN_JIRA)

# Endpoint raiz
@app.get("/")
def root():
    return {"message": "Hello World"}

# Novo endpoint para buscar dados do quadro
@app.get("/board")
def get_board():
    try:
        # Buscando os dados do quadro com board_id fixo
        board_data = jira_client.get_single_board(board_id=BOARD_ID)
        return board_data
    except Exception as e:
        # Logando o erro completo
        logger.error(f"Erro ao buscar o quadro: {str(e)}", exc_info=True)
        # Retornando um erro 500 em caso de falha
        raise HTTPException(status_code=500, detail=str(e))