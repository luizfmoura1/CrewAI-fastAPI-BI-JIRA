def rework_search(data: dict) -> list:
    """
    Retorna informações específicas sobre os cards (issues) do Jira, incluindo:
    - Chave do card (key)
    - Changelog (histórico de alterações)
    - Nome do status (status -> name)
    - Categoria do status (status -> statusCategory)
    - Story Points (customfield_10106)
    - Nome do desenvolvedor (assignee -> displayName)
    - Data de criação (created)
    - Data de atualização (updated)
    """
    cards = []
    for issue in data['issues']:
        # Extraindo informações básicas do issue
        issue_key = issue.get('key')
        
        # Extraindo o changelog (histórico de alterações)
        changelog = issue.get('changelog', {}).get('histories', [])
        
        # Extraindo o status do card
        status = issue.get('fields', {}).get('status', {})
        status_name = status.get('name')
        status_category = status.get('statusCategory', {}).get('name')
        
        # Extraindo story points
        story_points = issue.get('fields', {}).get('customfield_10106', 0)
        
        # Extraindo o nome do desenvolvedor (assignee)
        assignee = issue.get('fields', {}).get('assignee', {})
        developer_name = assignee.get('displayName') if assignee else "Não atribuído"
        
        # Extraindo as datas de criação e atualização
        created = issue.get('fields', {}).get('created')
        updated = issue.get('fields', {}).get('updated')
        
        # Adicionando os dados ao card
        card_info = {
            'key': issue_key,
            'changelog': changelog,
            'status': {
                'name': status_name,
                'statusCategory': status_category
            },
            'story_points': story_points,
            'assignee': {
                'displayName': developer_name
            },
            'created': created,
            'updated': updated
        }
        cards.append(card_info)
    
    return cards