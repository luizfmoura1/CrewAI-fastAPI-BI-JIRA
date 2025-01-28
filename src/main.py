from src.agents.sp_agent import create_story_agent
from src.utils.sp_search import sp_search

def main(data: dict) -> list:
    rework = sp_search(data)
    sp_analysis = create_story_agent({'data': rework})
    return sp_analysis
    