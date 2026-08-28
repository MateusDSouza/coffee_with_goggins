from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class MessageLog(SQLModel, table=True):
    """Database representation of a sent message."""

    id: int | None = Field(default=None, primary_key=True)
    contact_name: str
    phone_number: str
    message: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = Field(default="SENT")
