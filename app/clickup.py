import os

import httpx

BASE_URL = "https://api.clickup.com/api/v2"


class ClickUpError(Exception):
    pass


class ClickUpClient:
    def __init__(self) -> None:
        self.token = os.environ["CLICKUP_API_TOKEN"]
        self.workspace_id = os.environ["CLICKUP_WORKSPACE_ID"]
        self.http = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": self.token},
            timeout=30.0,
        )

    def _get(self, path: str, params: dict | None = None) -> dict:
        response = self.http.get(path, params=params)
        if response.status_code == 401:
            raise ClickUpError("ClickUp rejected the token")
        if response.status_code == 429:
            raise ClickUpError("ClickUp rate limit reached, try again shortly")
        if response.status_code >= 400:
            raise ClickUpError(
                f"ClickUp returned {response.status_code} for {path}"
            )
        return response.json()

    def get_workspace(self) -> dict | None:
        data = self._get("/team")
        for team in data.get("teams", []):
            if str(team.get("id")) == str(self.workspace_id):
                return team
        return None

    def get_task_page(self, page: int = 0) -> dict:
        return self._get(
            f"/team/{self.workspace_id}/task",
            params={
                "page": page,
                "include_closed": "true",
                "subtasks": "true",
            },
        )