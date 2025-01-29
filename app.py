from fastapi import FastAPI, HTTPException
from src.utils.jira_client import JiraClient
from dotenv import load_dotenv
from src.main import main
import os
import logging

from src.utils.rework_search import filter_reprovado_entries

# Configuração de logs e .env
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
load_dotenv()

# Variáveis do Jira
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
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
    try:
        board_data = jira_client.get_single_board(board_id, sprint_id)
        issues = board_data.get("issues", [])
        
        all_reprovados = []
        issues_with_changelogs = []
        
        for issue in issues:
            issue_key = issue.get("key")
            dev = issue.get('fields', {}).get('customfield_10172', 'Não definido')
            
            if not issue_key:
                continue
                
            try:
                changelog_response = jira_client.get_issue_changelog(issue_key)
                filtered = filter_reprovado_entries(
                    issue_key=issue_key,
                    dev=dev,
                    changelog_data=changelog_response
                )
                
                # Popula AMBAS as listas
                issues_with_changelogs.append({
                    "issue": issue,
                    "reprovado_entries": filtered
                })
                all_reprovados.extend(filtered)
                
            except Exception as ex:
                logger.error(f"Falha ao buscar changelog: {ex}", exc_info=True)
                continue

        from src.agents.rework_agent import create_rework_agent
        rework_analysis = create_rework_agent(all_reprovados)

        return {
            "board_id": board_id,
            "sprint_id": sprint_id,
            "raw_data": issues_with_changelogs,  # Dados brutos completos
            "analysis": rework_analysis  # Resultado processado
        }

    except Exception as e:
        logger.error(f"Erro: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
