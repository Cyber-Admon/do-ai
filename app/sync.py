from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clickup import ClickUpClient
from app.db import engine
from app.models import Task


def _parse_due(value) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)


def _clean_assignees(raw) -> list:
    return [
        {
            "id": person.get("id"),
            "username": person.get("username"),
            "email": person.get("email"),
        }
        for person in (raw or [])
    ]


def sync_tasks() -> dict:
    client = ClickUpClient()
    now = datetime.now(timezone.utc)
    created = 0
    updated = 0
    page = 0

    with Session(engine) as session:
        while True:
            data = client.get_task_page(page)
            tasks = data.get("tasks", [])

            for item in tasks:
                clickup_id = str(item["id"])
                row = session.scalar(
                    select(Task).where(Task.clickup_id == clickup_id)
                )
                if row is None:
                    row = Task(clickup_id=clickup_id, source="clickup")
                    session.add(row)
                    created += 1
                else:
                    updated += 1

                row.title = (item.get("name") or "(untitled)")[:500]
                row.description = item.get("text_content") or item.get(
                    "description"
                )
                row.status = (item.get("status") or {}).get("status")
                row.assignees = _clean_assignees(item.get("assignees"))
                row.due_at = _parse_due(item.get("due_date"))
                row.url = item.get("url")
                row.last_synced_at = now

            if data.get("last_page", True) or not tasks:
                break
            page += 1

        session.commit()

    return {"created": created, "updated": updated, "pages": page + 1}