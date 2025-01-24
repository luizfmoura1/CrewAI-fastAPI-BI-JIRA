def rework_search(data: dict) -> list:
    """
    Retorna informações específicas sobre os cards (issues) do Jira, incluindo:
    - Nome do desenvolvedor (assignee)
    - ID do card (id)
    - Chave do card (key)
    - Story point (id da prioridade)
    - Status do card (status)
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
        
        # Extraindo o status do card
        status = issue.get('fields', {}).get('status', {})
        status_name = status.get('name')  # Nome do status (ex: "Cancelado")
        status_id = status.get('id')  # ID do status
        status_category = status.get('statusCategory', {}).get('name')  # Categoria do status (ex: "Done")
        
        # Adicionando os dados ao card
        card_info = {
            'id': issue_id,
            'key': issue_key,
            'developer': developer_name,
            'story_points': story_points,
            'status': {
                'name': status_name,
                'id': status_id,
                'category': status_category
            }
        }
        cards.append(card_info)
    
    return cards