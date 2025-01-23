def rework_search(data: dict) -> list:
    """
    Retorna todas as informações disponíveis sobre os cards (issues) do Jira.
    """
    cards = []
    for issue in data['issues']:
        # Adiciona todos os dados da issue ao card
        cards.append(issue)
    return cards