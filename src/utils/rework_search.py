def rework_search(data: dict) -> list:
    """
    Retorna informações específicas sobre os cards (issues) do Jira, incluindo:
    - Nome do desenvolvedor (assignee)
    - ID do card (id)
    - Story point (id da prioridade)
    """
    cards = []
    for issue in data['issues']:
        # Extraindo informações básicas do issue
        issue_id = issue.get('id')  # ID do card
        issue_key = issue.get('key')  # Chave do card (ex: WEB-291)
        
        # Extraindo o nome do desenvolvedor (assignee)
        assignee = issue.get('fields', {}).get('assignee', {})
        developer_name = assignee.get('displayName') if assignee else "Não atribuído"
        
        # Extraindo o story point (id da prioridade)
        priority = issue.get('fields', {}).get('priority', {})
        story_points = priority.get('id')  # Obtém o ID da prioridade como story point
        
        # Adicionando os dados ao card
        card_info = {
            'id': issue_id,
            'key': issue_key,
            'developer': developer_name,
            'story_points': story_points
        }
        cards.append(card_info)
    
    return cards