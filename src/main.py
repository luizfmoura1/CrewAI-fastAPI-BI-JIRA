from src.agents.sp_agent import create_story_agent
from src.utils.sp_search import sp_search
from src.utils.rework_search import filter_reprovado_entries

def main(data: dict) -> list:
    
    cards = sp_search(data)
    
    for card in cards:
        card['reprovado_entries'] = filter_reprovado_entries(
            issue_key=card['key'],
            dev=card['dev'],
            changelog_data={'changelog': {'histories': card['changelog']}},
            assignee=card.get('assignee', {})
        )
    
    return create_story_agent({'data': cards})