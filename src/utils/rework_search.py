def filter_reprovado_entries(
    issue_key: str, 
    dev: str, 
    changelog_data: dict,
    assignee: dict  # Novo parâmetro com dados completos do assignee
) -> list:
    """
    Filtra entradas 'Reprovado' usando o responsável real (assignee)
    Retorna lista com:
    - Key do card
    - Assignee (responsável)
    - Desenvolvedor (customfield_10172)
    - Quem reprovou (author)
    - Datas e status
    """
    changelog = changelog_data.get('changelog', {}).get('histories', [])
    reprovado_entries = []
    
    for history in changelog:
        for item in history.get('items', []):
            if item.get('toString') == 'Reprovado':
                # Extrai informações do assignee
                assignee_name = assignee.get('displayName', 'Não atribuído')
                assignee_account_id = assignee.get('accountId')
                
                entry = {
                    'card_key': issue_key,
                    'responsavel': assignee_name,  # Usa o assignee aqui
                    'account_id': assignee_account_id,
                    'desenvolvedor': dev,
                    'quem_reprovou': history.get('author', {}).get('displayName'),  # Mantém quem executou a ação
                    'data_mudanca': history.get('created'),
                    'status_anterior': item.get('fromString'),
                    'status_novo': item.get('toString'),
                    'avatar_url': assignee.get('avatarUrls', {}).get('48x48')  # Extrai avatar se necessário
                }
                reprovado_entries.append(entry)
    
    return reprovado_entries