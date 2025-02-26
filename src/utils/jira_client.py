import requests

class JiraClient:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url
        self.auth = (email, api_token)

    def get_single_board(self, board_id, sprint_id):
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}/issue"
        params = {
            "jql": "status NOT IN (CANCELADO)",
            "fields": "customfield_10106,customfield_10172,assignee,status,created"
        }
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao buscar o board/sprint: {response.status_code} - {response.text}")

    def get_issue_changelog(self, issue_id) -> dict:
        url = f"{self.base_url}/rest/api/2/issue/{issue_id}"
        params = {"expand": "changelog"}
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao buscar changelog: {response.status_code} - {response.text}")

    def get_all_boards(self):
        url = f"{self.base_url}/rest/agile/1.0/board"
        headers = {"Accept": "application/json"}
        boards = []
        start_at = 0
        max_results = 50
        while True:
            params = {"startAt": start_at, "maxResults": max_results}
            response = requests.get(url, headers=headers, params=params, auth=self.auth)
            if response.status_code != 200:
                raise Exception(f"Erro ao buscar boards: {response.status_code} - {response.text}")
            data = response.json()
            boards.extend(data.get("values", []))
            if data.get("isLast", True):
                break
            start_at += max_results
        return boards

    def get_sprints_by_board(self, board_id):
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
        headers = {"Accept": "application/json"}
        sprints = []
        start_at = 0
        max_results = 50
        while True:
            params = {"startAt": start_at, "maxResults": max_results}
            response = requests.get(url, headers=headers, params=params, auth=self.auth)
            if response.status_code != 200:
                raise Exception(f"Erro ao buscar sprints para o board {board_id}: {response.status_code} - {response.text}")
            data = response.json()
            sprints.extend(data.get("values", []))
            if data.get("isLast", True):
                break
            start_at += max_results
        return sprints
