# src/utils/progression_search.py

def extract_card_progression(
    issue_key: str,
    dev: str,
    sp: float,
    changelog_data: dict,
    assignee: dict
) -> list:
    """
    Extrai o histórico completo de transições de status de um card.
    """
    changelog = changelog_data.get('changelog', {}).get('histories', [])
    progression_entries = []
    
    # Percorre todo o histórico de alterações do card
    for history in changelog:
        # Para cada evento de alteração, verifica os itens que foram mudados
        for item in history.get('items', []):
            # Nosso foco é apenas quando o campo 'status' foi alterado
            if item.get('field', '').lower() == 'status':
                
                assignee_name = assignee.get('displayName', 'Não atribuído')
                author_name = history.get('author', {}).get('displayName', 'N/A')

                entry = {
                    'card_key': issue_key,
                    'data_mudanca': history.get('created'),
                    'status_antigo': item.get('fromString', 'N/A'),
                    'status_novo': item.get('toString', 'N/A'),
                    'responsavel_card': assignee_name,
                    'autor_mudanca': author_name,
                    'sp': sp,
                    'desenvolvedor': dev,
                }
                progression_entries.append(entry)
    
    return progression_entries