import requests

class JiraClient:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url
        self.auth = (email, api_token)  # Autenticação básica (email + API token)

    def get_single_board(self, board_id):
        """
        Obtém os dados de um quadro (board) específico no Jira.
        """
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}"
        headers = {
            "Accept": "application/json"
        }
        
        # Fazendo a requisição GET
        response = requests.get(url, headers=headers, auth=self.auth)
        
        # Verificando se a requisição foi bem-sucedida
        if response.status_code == 200:
            return response.json()  # Retorna os dados do quadro
        else:
            raise Exception(f"Erro ao buscar o quadro: {response.status_code} - {response.text}")