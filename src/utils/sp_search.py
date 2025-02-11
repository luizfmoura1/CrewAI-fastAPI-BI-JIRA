def sp_search(data: dict) -> list:
    cards = []
    for issue in data['issues']:
        issue_key = issue.get('key')
        story_points = issue.get('fields', {}).get('customfield_10106', 0)
        dev = issue.get('fields', {}).get('customfield_10172', 'Não definido')
        assignee = issue.get('fields', {}).get('assignee', {})
        developer_name = assignee.get('displayName') if assignee else "Não atribuído"
        created = issue.get('fields', {}).get('created')
        
        card_info = {
            'key': issue_key,
            'changelog': issue.get('changelog', {}).get('histories', []),
            'story_points': story_points,
            'dev': dev,
            'assignee': {
                'displayName': developer_name
            },
            'created': created
        }
        cards.append(card_info)
        print(cards)
    
    return cards
