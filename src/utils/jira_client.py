import requests

class JiraClient:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url
        self.auth = (email, api_token)  # Autenticação básica (email + API token)

    def get_single_board(self, board_id, sprint_id):
        """
        Obtém os dados de um quadro (board) e uma sprint específica no Jira,
        incluindo todos os cards (ativos e cancelados).
        """
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}/issue"
        
        # Parâmetros para incluir todos os cards, independentemente do status
        params = {
            "jql": "status NOT IN (CANCELADO)",  # Filtra apenas cards ativos
            "maxResults": 100,
            "fields": "*all"
        }
        
        headers = {
            "Accept": "application/json"
        }
        
        # Fazendo a requisição GET
        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        
        # Verificando se a requisição foi bem-sucedida
        if response.status_code == 200:
            return response.json()  # Retorna os dados do quadro e da sprint
        else:
            raise Exception(f"Erro ao buscar o quadro/sprint: {response.status_code} - {response.text}")
        
    def get_issue_changelog(self, issue_id):
        """
        Retorna os dados de uma issue específica, incluindo o changelog.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_id}"
        params = {
            "expand": "changelog"
        }
        headers = {
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao buscar o changelog da issue: {response.status_code} - {response.text}")