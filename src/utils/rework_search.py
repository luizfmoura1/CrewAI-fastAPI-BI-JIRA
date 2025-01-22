def rework_search(data: dict) -> list:
    cards = []
    for i in data['issues']:
        card_id = i['id']
        priority_id = i['fields']['priority']['id'] if i['fields'].get('priority') else None
        assignee = i['fields']['assignee']['displayName'] if i['fields'].get('assignee') else None

        cards.append({
            'id': card_id,
            'priority_id': priority_id,
            'assignee': assignee
        })
    return cards