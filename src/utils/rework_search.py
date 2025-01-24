import requests

class JiraClient:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url
        self.auth = (email, api_token)  # Autenticação básica (email + API token)

    def get_issue_changelog(self, issue_key):
        """
        Obtém o changelog (histórico de alterações) de um issue específico.
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/changelog"
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, auth=self.auth)
        
        if response.status_code == 200:
            return response.json()  # Retorna o changelog do issue
        else:
            raise Exception(f"Erro ao buscar o changelog: {response.status_code} - {response.text}")

    def rework_search(self, data: dict) -> list:
        """
        Retorna informações específicas sobre os cards (issues) do Jira, incluindo:
        - key: Chave do card (ex: WEB-291)
        - changelog: Histórico de alterações do card
        - status -> name: Nome do status (ex: "Cancelado")
        - status -> statusCategory: Categoria do status (ex: "Done")
        - priority -> id: ID da prioridade
        - assignee -> displayName: Nome do desenvolvedor atribuído
        - created: Data de criação do card
        - updated: Data da última atualização
        """
        cards = []
        for issue in data['issues']:
            # Extraindo a chave do issue
            issue_key = issue.get('key')
            
            # Extraindo o changelog do issue
            changelog = self.get_issue_changelog(issue_key)
            
            # Extraindo o status do card
            status = issue.get('fields', {}).get('status', {})
            status_name = status.get('name')  # Nome do status (ex: "Cancelado")
            status_category = status.get('statusCategory', {}).get('name')  # Categoria do status (ex: "Done")
            
            # Extraindo a prioridade do card
            priority = issue.get('fields', {}).get('priority', {})
            priority_id = priority.get('id')  # ID da prioridade
            
            # Extraindo o nome do desenvolvedor (assignee)
            assignee = issue.get('fields', {}).get('assignee', {})
            developer_name = assignee.get('displayName') if assignee else "Não atribuído"
            
            # Extraindo as datas de criação e atualização
            created = issue.get('fields', {}).get('created')  # Data de criação
            updated = issue.get('fields', {}).get('updated')  # Data da última atualização
            
            # Adicionando os dados ao card
            card_info = {
                'key': issue_key,
                'changelog': changelog,
                'status': {
                    'name': status_name,
                    'category': status_category
                },
                'priority': {
                    'id': priority_id
                },
                'assignee': developer_name,
                'created': created,
                'updated': updated
            }
            cards.append(card_info)
        
        return cards