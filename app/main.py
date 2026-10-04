from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.db import engine

app = FastAPI(title="Do")


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