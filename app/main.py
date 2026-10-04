import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.clickup import ClickUpClient, ClickUpError
from app.db import engine
from app.models import Task
from app.slack_bot import start_slack
from app.sync import sync_tasks

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_slack()
    yield


app = FastAPI(title="Do", lifespan=lifespan)


@app.get("/")
def root():
    return {"name": "Do", "status": "running"}


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unreachable")
    return {"status": "ok", "database": "connected"}


@app.get("/clickup/check")
def clickup_check():
    try:
        client = ClickUpClient()
        workspace = client.get_workspace()
        if workspace is None:
            raise HTTPException(
                status_code=404,
                detail="Token works, but no workspace matches CLICKUP_WORKSPACE_ID",
            )
        page = client.get_task_page(0)
    except (ClickUpError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return {
        "workspace": workspace.get("name"),
        "members": len(workspace.get("members", [])),
        "tasks_on_first_page": len(page.get("tasks", [])),
        "more_pages": not page.get("last_page", True),
    }


@app.post("/clickup/sync")
def clickup_sync():
    try:
        return sync_tasks()
    except (ClickUpError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/tasks")
def list_tasks():
    with Session(engine) as session:
        rows = session.scalars(
            select(Task).order_by(Task.due_at.asc().nulls_last(), Task.id)
        ).all()

    return {
        "count": len(rows),
        "tasks": [
            {
                "title": row.title,
                "status": row.status,
                "due_at": row.due_at.isoformat() if row.due_at else None,
                "assignees": [a.get("username") for a in row.assignees],
                "source": row.source,
            }
            for row in rows
        ],
    }