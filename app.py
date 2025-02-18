from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import logging

# Importa os módulos internos do projeto
from src.utils.jira_client import JiraClient
from src.main import main  # Certifique-se de que essa função está implementada
from src.utils.rework_search import filter_reprovado_entries

# Carrega variáveis de ambiente e configura o logging
load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Variáveis de ambiente do Jira
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
API_TOKEN_JIRA = os.getenv("API_TOKEN_JIRA")

if not API_TOKEN_JIRA:
    logger.error("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")
    raise ValueError("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")

# Criação da aplicação FastAPI
app = FastAPI()

# Instancia o cliente Jira
jira_client = JiraClient(base_url=BASE_URL, email=EMAIL, api_token=API_TOKEN_JIRA)

@app.get("/JIRA_analitycs")
def get_analitycs(board_id: str, sprint_id: str) -> dict:
    """
    Consulta as issues de um board e sprint específicos e retorna a análise processada.
    """
    try:
        board_data = jira_client.get_single_board(board_id, sprint_id)
        response = main(board_data)
        
        from src.agents.sp_agent import create_story_agent  # Certifique-se de que o agente está implementado
        sp_analysis = create_story_agent(board_data)

        return {
            "board_id": board_id,
            "sprint_id": sprint_id,
            "raw_data": board_data,  # Dados brutos extraídos do Jira
            "analysis": {
                "processed_data": [response],  # Dados processados pela função `main()`
                "sp_analysis": sp_analysis      # Resultado da análise do agente
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar o board: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/JIRA_analitycs_with_changelogs")
def get_analitycs_with_changelogs(board_id: str, sprint_id: str) -> dict:
    """
    Consulta as issues de um board/sprint e processa os changelogs para identificar entradas de reprovação.
    """
    try:
        board_data = jira_client.get_single_board(board_id, sprint_id)
        issues = board_data.get("issues", [])
        
        all_reprovados = []
        issues_with_changelogs = []
        
        for issue in issues:
            issue_key = issue.get("key")
            fields = issue.get("fields", {})
            
            # Extração dos dados relevantes
            assignee = fields.get("assignee", {})
            dev = fields.get("customfield_10172", "Não definido")
            sp = fields.get("customfield_10106", 0)
            
            if not issue_key:
                continue
                
            try:
                changelog_response = jira_client.get_issue_changelog(issue_key)
                filtered = filter_reprovado_entries(
                    issue_key=issue_key,
                    dev=dev,
                    sp=sp,
                    changelog_data=changelog_response,
                    assignee=assignee
                )
                
                issues_with_changelogs.append({
                    "issue": issue,
                    "reprovado_entries": filtered
                })
                all_reprovados.extend(filtered)
                
            except Exception as ex:
                logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                continue

        from src.agents.rework_agent import create_rework_agent  # Certifique-se de que o agente está implementado
        rework_analysis = create_rework_agent(all_reprovados)
        
        return {
            "board_id": board_id,
            "sprint_id": sprint_id,
            "analysis": {
                "llm_analysis": rework_analysis.get("llm_analysis", "Análise não disponível"),
                "charts_data": rework_analysis.get("charts_data", {
                    "conclusoes": [],
                    "reprovacoes": [],
                    "metrics": {
                        "total_concluidos": 0,
                        "total_reprovados": 0,
                        "total_reprovações": 0
                    }
                })
            }
        }

    except Exception as e:
        logger.error(f"Erro durante a análise com changelogs: {e}", exc_info=True)
        return {
            "error": str(e),
            "analysis": {
                "llm_analysis": "Erro na análise",
                "charts_data": {
                    "conclusoes": [],
                    "reprovacoes": [],
                    "metrics": {
                        "total_concluidos": 0,
                        "total_reprovados": 0,
                        "total_reprovas": 0
                    }
                }
            }
        }


@app.get("/boards")
def list_boards():
    """
    Endpoint para listar todos os boards acessíveis pelo usuário.
    """
    try:
        boards = jira_client.get_all_boards()
        return {"boards": boards}
    except Exception as e:
        logger.error(f"Erro ao listar boards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/boards/{board_id}/sprints")
def list_sprints(board_id: str):
    """
    Endpoint para listar todos os sprints de um board específico.
    """
    try:
        sprints = jira_client.get_sprints_by_board(board_id)
        return {"board_id": board_id, "sprints": sprints}
    except Exception as e:
        logger.error(f"Erro ao listar sprints para o board {board_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/JIRA_all_analytics")
def get_all_analytics():
    """
    Endpoint que consulta todos os boards e, para cada board, todos os sprints,
    realizando a análise de cada combinação por meio do rework agent.
    """
    results = []
    try:
        boards = jira_client.get_all_boards()
        for board in boards:
            board_id = board.get("id")
            sprints = jira_client.get_sprints_by_board(board_id)
            for sprint in sprints:
                sprint_id = sprint.get("id")
                board_data = jira_client.get_single_board(board_id, sprint_id)
                issues = board_data.get("issues", [])
                all_reprovados = []
                
                for issue in issues:
                    issue_key = issue.get("key")
                    fields = issue.get("fields", {})
                    assignee = fields.get("assignee", {})
                    dev = fields.get("customfield_10172", "Não definido")
                    sp = fields.get("customfield_10106", 0)
                    
                    if not issue_key:
                        continue
                        
                    try:
                        changelog_response = jira_client.get_issue_changelog(issue_key)
                        filtered = filter_reprovado_entries(
                            issue_key=issue_key,
                            dev=dev,
                            sp=sp,
                            changelog_data=changelog_response,
                            assignee=assignee
                        )
                        all_reprovados.extend(filtered)
                    except Exception as ex:
                        logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                        continue
                        
                from src.agents.rework_agent import create_rework_agent  # Processa os dados com o rework agent
                rework_analysis = create_rework_agent(all_reprovados)
                
                results.append({
                    "board_id": board_id,
                    "sprint_id": sprint_id,
                    "analysis": rework_analysis
                })
        return {"results": results}
    except Exception as e:
        logger.error(f"Erro ao buscar analytics para todos os boards e sprints: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
