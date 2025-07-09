# src/utils/jira_client.py

import requests

class JiraClient:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url
        self.auth = (email, api_token)

    def get_issues_by_board(self, board_id):
        """Busca todas as issues de um board (backlog e colunas)."""
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/issue"
        params = {
            "jql": "status NOT IN (CANCELADO)",
            "fields": "customfield_10106,customfield_10172,assignee,status,created"
        }
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        response.raise_for_status()
        return response.json().get("issues", [])

    def get_issue_changelog(self, issue_id) -> dict:
        """Busca o histórico de mudanças (changelog) de um card específico."""
        url = f"{self.base_url}/rest/api/2/issue/{issue_id}"
        params = {"expand": "changelog"}
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_all_boards(self):
        """Busca todos os boards disponíveis."""
        url = f"{self.base_url}/rest/agile/1.0/board"
        headers = {"Accept": "application/json"}
        boards = []
        start_at = 0
        max_results = 50
        while True:
            params = {"startAt": start_at, "maxResults": max_results}
            response = requests.get(url, headers=headers, params=params, auth=self.auth)
            response.raise_for_status()
            data = response.json()
            boards.extend(data.get("values", []))
            if data.get("isLast", True):
                break
            start_at += max_results
        return boards