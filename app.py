# app.py

from fastapi import FastAPI, HTTPException
from src.utils.jira_client import JiraClient
from dotenv import load_dotenv
from src.main import main
import os
import logging

# Configuração de logs e .env
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
load_dotenv()

# Variáveis do Jira
BASE_URL = "https://ngosolucoes.atlassian.net"
EMAIL = "master@oppem.com.br"
API_TOKEN_JIRA = os.getenv("API_TOKEN_JIRA")

if not API_TOKEN_JIRA:
    logger.error("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")
    raise ValueError("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")

# Cria a aplicação FastAPI e o cliente Jira
app = FastAPI()
jira_client = JiraClient(base_url=BASE_URL, email=EMAIL, api_token=API_TOKEN_JIRA)

@app.get("/JIRA_analitycs")
def get_analitycs(board_id: str, sprint_id: str) -> dict:
    try:
        board_data = jira_client.get_single_board(board_id, sprint_id)
        response = main(board_data)
        final_content = {'data': [response]}
        return final_content
    except Exception as e:
        logger.error(f"Erro ao buscar o quadro: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/JIRA_analitycs_with_changelogs")
def get_analitycs_with_changelogs(board_id: str, sprint_id: str) -> dict:
    """
    Endpoint que retorna as issues de um board/sprint já acompanhadas de seus changelogs.
    """
    try:
        # 1. Obter os dados do quadro e sprint (issues, etc.)
        board_data = jira_client.get_single_board(board_id, sprint_id)
        
        issues = board_data.get("issues", [])
        
        # 2. Para cada issue, buscar o changelog chamando o novo método do JiraClient
        issues_with_changelogs = []
        for issue in issues:
            issue_key = issue.get("key")
            if issue_key:
                try:
                    changelog_response = jira_client.get_issue_changelog(issue_key)
                    # Anexa o changelog (ou parte dele) aos dados da issue
                    issues_with_changelogs.append({
                        "issue": issue,  # dados básicos da issue
                        "changelog": changelog_response.get("changelog")  
                    })
                except Exception as ex:
                    logger.error(f"Falha ao buscar changelog da issue {issue_key}: {ex}", exc_info=True)
                    # Dependendo da necessidade, você pode:
                    # - Continuar (pular) ou 
                    # - Interromper e lançar HTTPException
                    # Aqui vamos apenas pular para não travar todas as issues
                    continue

        # 3. Se quiser processar com a função main (ou algum agente), faça aqui.
        #    Ou retorne diretamente.

        return {
            "board_id": board_id,
            "sprint_id": sprint_id,
            "issues_count": len(issues_with_changelogs),
            "data": issues_with_changelogs
        }
    except Exception as e:
        logger.error(f"Erro ao buscar quadro/sprint e changelogs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
