from src.agents.sp_agent import create_story_agent
from src.utils.sp_search import sp_search
from src.utils.rework_search import filter_reprovado_entries  # Novo

def main(data: dict) -> list:
    rework = sp_search(data)
    
    # Adiciona as entradas de reprovação filtradas
    for card in rework:
        card['reprovado_entries'] = filter_reprovado_entries(
            issue_key=card['key'],
            dev=card['dev'],
            changelog_data={'changelog': {'histories': card['changelog']}}
        )
    
    return create_story_agent({'data': rework})