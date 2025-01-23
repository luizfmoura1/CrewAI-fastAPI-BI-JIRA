from src.agents.retrabalho_agent import create_retrabalho_agent
from src.agents.story_points_agent import create_story_points_agent
from src.utils.rework_search import rework_search

def main(data: dict, sprint_id: int = None) -> list:
    """
    Função principal para processar os dados do Jira.
    
    Args:
        data (dict): Dados do quadro (board) do Jira.
        sprint_id (int, optional): ID do sprint. Defaults to None.
    
    Returns:
        list: Resultado da análise de retrabalho.
    """
    rework = rework_search(data)
    rework_analysis = create_retrabalho_agent(rework)
    return rework_analysis