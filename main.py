from fastapi import FastAPI, HTTPException
from utils.jira_client import JiraClient
from dotenv import load_dotenv
import os

# Carregando as variáveis de ambiente
load_dotenv()

# Configurações do Jira (substitua pelos seus valores)
BASE_URL = "https://ngosolucoes.atlassian.net"  # Substitua pelo seu domínio do Jira
EMAIL = "master@oppem.com.br"  # Substitua pelo seu email
API_TOKEN_JIRA = os.getenv("API_TOKEN")  # Carregado do arquivo .env
BOARD_ID = 24  # Usando o board_id fixo

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
        # Retornando um erro 500 em caso de falha
        raise HTTPException(status_code=500, detail=str(e))
