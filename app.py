from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import requests
from src.utils.jira_client import JiraClient
from src.main import main
from src.utils.rework_search import filter_reprovado_entries

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
API_TOKEN_JIRA = os.getenv("API_TOKEN_JIRA")
if not API_TOKEN_JIRA:
    logger.error("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")
    raise ValueError("API_TOKEN_JIRA não foi carregado corretamente do arquivo .env")
app = FastAPI()
jira_client = JiraClient(base_url=BASE_URL, email=EMAIL, api_token=API_TOKEN_JIRA)

@app.get("/JIRA_all_analytics")
def get_all_analytics(num_sprints: int = 2):
    def process_all_analytics(num_sprints: int) -> dict:
        try:
            boards = jira_client.get_all_boards()
            unique_sprints = {}
            for board in boards:
                board_id = board.get("id")
                try:
                    sprints = jira_client.get_sprints_by_board(board_id)
                except Exception as e:
                    if "O quadro não aceita sprints" in str(e):
                        logger.warning(f"Board {board_id} não aceita sprints. Pulando esse board.")
                        continue
                    else:
                        raise
                for sprint in sprints:
                    sprint_id = sprint.get("id")
                    if sprint_id not in unique_sprints:
                        sprint["boards"] = [board_id]
                        unique_sprints[sprint_id] = sprint
                    else:
                        if board_id not in unique_sprints[sprint_id].get("boards", []):
                            unique_sprints[sprint_id]["boards"].append(board_id)
            all_sprints = list(unique_sprints.values())
            if all_sprints:
                if "startDate" in all_sprints[0] and all_sprints[0].get("startDate"):
                    sorted_sprints = sorted(all_sprints, key=lambda s: s.get("startDate", ""), reverse=True)
                else:
                    sorted_sprints = all_sprints
                selected_sprints = sorted_sprints[:num_sprints]
            else:
                selected_sprints = []
            aggregated_cards = []
            sprint_info = []
            for sprint in selected_sprints:
                sprint_id = sprint.get("id")
                boards_list = sprint.get("boards", [])
                for board_id in boards_list:
                    board_data = jira_client.get_single_board(board_id, sprint_id)
                    issues = board_data.get("issues", [])
                    for issue in issues:
                        issue_key = issue.get("key")
                        fields = issue.get("fields", {})
                        assignee = fields.get("assignee") or {}
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
                            aggregated_cards.extend(filtered)
                        except Exception as ex:
                            logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                            continue
                sprint_info.append({"sprint_id": sprint_id, "boards": boards_list})
            from src.agents.rework_agent import create_rework_agent
            rework_analysis = create_rework_agent(aggregated_cards)
            return {
                "sprints": sprint_info,
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
            logger.error(f"Erro ao buscar analytics para todos os boards e sprints: {e}", exc_info=True)
            raise Exception(str(e))
    try:
        return process_all_analytics(num_sprints)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/JIRA_daily_all_analytics")
def get_daily_all_analytics(num_sprints: int = 2):
    try:
        boards = jira_client.get_all_boards()
        unique_sprints = {}
        for board in boards:
            board_id = board.get("id")
            try:
                sprints = jira_client.get_sprints_by_board(board_id)
            except Exception as e:
                if "O quadro não aceita sprints" in str(e):
                    logger.warning(f"Board {board_id} não aceita sprints. Pulando esse board.")
                    continue
                else:
                    raise
            for sprint in sprints:
                sprint_id = sprint.get("id")
                if sprint_id not in unique_sprints:
                    sprint["boards"] = [board_id]
                    unique_sprints[sprint_id] = sprint
                else:
                    if board_id not in unique_sprints[sprint_id].get("boards", []):
                        unique_sprints[sprint_id]["boards"].append(board_id)
        all_sprints = list(unique_sprints.values())
        if all_sprints:
            if "startDate" in all_sprints[0] and all_sprints[0].get("startDate"):
                sorted_sprints = sorted(all_sprints, key=lambda s: s.get("startDate", ""), reverse=True)
            else:
                sorted_sprints = all_sprints
            selected_sprints = sorted_sprints[:num_sprints]
        else:
            selected_sprints = []

        aggregated_cards = []
        for sprint in selected_sprints:
            sprint_id = sprint.get("id")
            boards_list = sprint.get("boards", [])
            for board_id in boards_list:
                board_data = jira_client.get_single_board(board_id, sprint_id)
                issues = board_data.get("issues", [])
                for issue in issues:
                    issue_key = issue.get("key")
                    if not issue_key:
                        continue
                    fields = issue.get("fields", {})
                    assignee = fields.get("assignee") or {}
                    dev = fields.get("customfield_10172", "Não definido")
                    sp = fields.get("customfield_10106", 0)
                    try:
                        changelog_response = jira_client.get_issue_changelog(issue_key)
                        filtered = filter_reprovado_entries(
                            issue_key=issue_key,
                            dev=dev,
                            sp=sp,
                            changelog_data=changelog_response,
                            assignee=assignee
                        )
                        aggregated_cards.extend(filtered)
                    except Exception as ex:
                        logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                        continue

        # Definir o período diário (apenas o dia atual)
        today_date = datetime.now().date()
        start_date = datetime.combine(today_date, datetime.min.time())
        end_date = datetime.combine(today_date, datetime.max.time())

        from src.agents.rework_agent import create_rework_agent
        rework_analysis = create_rework_agent(aggregated_cards, start_date=start_date, end_date=end_date)
        concl_cards = rework_analysis.get("charts_data", {}).get("conclusoes", [])
        total_story_points = sum(float(item.get("sp", 0)) for item in concl_cards)
        return {"daily_concluded_cards": concl_cards, "total_story_points": total_story_points}
    except Exception as e:
        logger.error(f"Erro ao buscar daily analytics para todos os boards e sprints: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/JIRA_analitycs")
def get_analitycs(board_id: str, sprint_id: str) -> dict:
    try:
        board_data = jira_client.get_single_board(board_id, sprint_id)
        response = main(board_data)
        from src.agents.sp_agent import create_story_agent 
        sp_analysis = create_story_agent(board_data)
        return {
            "board_id": board_id,
            "sprint_id": sprint_id,
            "raw_data": board_data,
            "analysis": {"processed_data": [response], "sp_analysis": sp_analysis}
        }
    except Exception as e:
        logger.error(f"Erro ao buscar o board: {str(e)}", exc_info=True)
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
                issues_with_changelogs.append({"issue": issue, "reprovado_entries": filtered})
                all_reprovados.extend(filtered)
            except Exception as ex:
                logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                continue
        from src.agents.rework_agent import create_rework_agent
        rework_analysis = create_rework_agent(all_reprovados)
        return {
            "board_id": board_id,
            "sprint_id": sprint_id,
            "analysis": {
                "llm_analysis": rework_analysis.get("llm_analysis", "Análise não disponível"),
                "charts_data": rework_analysis.get("charts_data", {
                    "conclusoes": [],
                    "reprovacoes": [],
                    "metrics": {"total_concluidos": 0, "total_reprovados": 0, "total_reprovações": 0}
                })
            }
        }
    except Exception as e:
        logger.error(f"Erro durante a análise com changelogs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/JIRA_analitycs_daily")
def get_analitycs_daily(board_id: str, sprint_id: str) -> dict:
    try:
        board_data = jira_client.get_single_board(board_id, sprint_id)
        issues = board_data.get("issues", [])
        aggregated_cards = []
        for issue in issues:
            issue_key = issue.get("key")
            if not issue_key:
                continue
            fields = issue.get("fields", {})
            assignee = fields.get("assignee") or {}
            dev = fields.get("customfield_10172", "Não definido")
            sp = fields.get("customfield_10106", 0)
            try:
                changelog_response = jira_client.get_issue_changelog(issue_key)
                filtered = filter_reprovado_entries(
                    issue_key=issue_key,
                    dev=dev,
                    sp=sp,
                    changelog_data=changelog_response,
                    assignee=assignee
                )
                aggregated_cards.extend(filtered)
            except Exception as ex:
                logger.error(f"Falha ao buscar changelog para a issue {issue_key}: {ex}", exc_info=True)
                continue

        # Definir o período como somente o dia atual
        today_date = datetime.now().date()
        start_date = datetime.combine(today_date, datetime.min.time())
        end_date = datetime.combine(today_date, datetime.max.time())

        from src.agents.rework_agent import create_rework_agent
        rework_analysis = create_rework_agent(aggregated_cards, start_date=start_date, end_date=end_date)
        # Extraindo somente as "conclusões" para a análise diária
        concl_cards = rework_analysis.get("charts_data", {}).get("conclusoes", [])
        total_story_points = sum(float(item.get("sp", 0)) for item in concl_cards)
        return {"concluded_cards": concl_cards, "total_story_points": total_story_points}
    except Exception as e:
        logger.error(f"Erro na análise diária específica: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/boards")
def list_boards():
    try:
        boards = jira_client.get_all_boards()
        return {"boards": boards}
    except Exception as e:
        logger.error(f"Erro ao listar boards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/boards/{board_id}/sprints")
def list_sprints(board_id: str):
    try:
        sprints = jira_client.get_sprints_by_board(board_id)
        return {"board_id": board_id, "sprints": sprints}
    except Exception as e:
        logger.error(f"Erro ao listar sprints para o board {board_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

list_boards = list_boards
list_sprints = list_sprints
get_all_analytics = get_all_analytics
get_daily_all_analytics = get_daily_all_analytics
get_analitycs = get_analitycs
get_analitycs_with_changelogs = get_analitycs_with_changelogs
get_analitycs_daily = get_analitycs_daily

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
