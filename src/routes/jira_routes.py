# src/routes/jira_routes.py

from fastapi import APIRouter, HTTPException
import logging

from src.utils.jira_client import JiraClient
from src.utils.progression_search import extract_card_progression
from src.agents.rework_agent import create_workflow_analysis_agent 
from src.config.config import BASE_URL, EMAIL, API_TOKEN_JIRA

jira_client = JiraClient(BASE_URL, EMAIL, API_TOKEN_JIRA)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/JIRA_card_progression")
def get_card_progression(board_id: str) -> dict:
    try:
        logger.info(f"Iniciando busca de todos os cards para o board {board_id}.")
        issues = jira_client.get_issues_by_board(board_id)
        
        if not issues:
            logger.warning(f"Nenhum card encontrado no Jira para o board {board_id}.")
            return {
                "board_id": board_id, "board_name": "N/A",
                "llm_analysis": "Diagnóstico: Nenhum card foi encontrado para este board no Jira. Verifique as permissões da sua chave de API ou se o board realmente contém issues.",
                "progression_data": []
            }

        card_progression_data = []
        for issue in issues:
            issue_key = issue.get("key")
            fields = issue.get("fields", {})
            assignee = fields.get("assignee", {})
            dev = fields.get("customfield_10172", "Não definido")
            sp = fields.get("customfield_10106", 0)
            
            if not issue_key: continue
            
            try:
                changelog_response = jira_client.get_issue_changelog(issue_key)
                progression = extract_card_progression(
                    issue_key=issue_key, dev=dev, sp=sp,
                    changelog_data=changelog_response, assignee=assignee
                )
                card_progression_data.extend(progression)
            except Exception as ex:
                logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                continue

        if not card_progression_data:
            logger.warning(f"Foram encontrados {len(issues)} cards, mas nenhum apresentou histórico de mudança de status relevante.")
            return {
                "board_id": board_id, "board_name": "N/A",
                "llm_analysis": f"Diagnóstico: {len(issues)} cards foram encontrados, mas nenhum continha um histórico de mudança de status para ser analisado. Isso pode acontecer com cards recém-criados ou que nunca foram movidos.",
                "progression_data": []
            }

        analysis_result = create_workflow_analysis_agent(card_progression_data)

        return {
            "board_id": board_id,
            "board_name": "N/A", # Simplificado
            "llm_analysis": analysis_result.get("llm_analysis", "Análise não disponível."),
            "progression_data": analysis_result.get("progression_data_for_display", [])
        }
    except Exception as e:
        logger.error(f"Erro durante a análise de progressão: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/boards")
def list_boards():
    try:
        boards = jira_client.get_all_boards()
        return {"boards": boards}
    except Exception as e:
        logger.error(f"Erro ao listar boards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))