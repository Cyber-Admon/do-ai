from datetime import datetime

from sqlalchemy import DateTime, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    clickup_id: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(100))
    assignees: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True
    )
    source: Mapped[str] = mapped_column(
        String(20), default="clickup", server_default="clickup"
    )
    url: Mapped[str | None] = mapped_column(String(500))
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )