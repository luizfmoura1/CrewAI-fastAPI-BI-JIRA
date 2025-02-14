def filter_reprovado_entries(
    issue_key: str,
    dev: str,
    sp: float,
    changelog_data: dict,
    assignee: dict
) -> list:
    changelog = changelog_data.get('changelog', {}).get('histories', [])
    reprovado_entries = []
    
    for history in changelog:
        for item in history.get('items', []):
            if item.get('toString') in ['Reprovado', 'Em produção', 'Em release', 'Em homologação']:
                assignee_name = assignee.get('displayName', 'Não atribuído')
                entry = {
                    'card_key': issue_key,
                    'responsavel': assignee_name,
                    'desenvolvedor': dev,
                    'status_novo': item.get('toString'),
                    'data_mudanca': history.get('created'),
                    'sp':sp,
                }
                reprovado_entries.append(entry)
    
    return reprovado_entries
