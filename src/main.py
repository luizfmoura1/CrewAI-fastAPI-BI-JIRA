from src.agents.retrabalho_agent import create_retrabalho_agent
from src.agents.story_points_agent import create_story_points_agent
from src.utils.rework_search import rework_search

def main(data: dict) -> list:
    rework = rework_search(data)
    rework_analysis = create_retrabalho_agent(rework)
    return rework
    