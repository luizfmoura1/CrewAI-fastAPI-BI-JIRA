def filter_reprovado_entries(issue_key: str, dev: str, changelog_data: dict) -> list:
    """
    Filtra as entradas do changelog onde 'toString' é "Reprovado".
    Retorna uma lista com:
    - Key do card
    - Responsável pela mudança
    - Desenvolvedor
    - Datas e status
    """
    changelog = changelog_data.get('changelog', {}).get('histories', [])
    reprovado_entries = []
    
    for history in changelog:
        for item in history.get('items', []):
            if item.get('toString') == 'Reprovado':
                entry = {
                    'card_key': issue_key,
                    'responsavel': history.get('author', {}).get('displayName'),
                    'desenvolvedor': dev,
                    'data_mudanca': history.get('created'),
                    'status_anterior': item.get('fromString'),
                    'status_novo': item.get('toString')
                }
                reprovado_entries.append(entry)
    
    return reprovado_entries