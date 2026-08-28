# db/database.py
from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel, create_engine

# SQLite database file stored locally
sqlite_file_name = "messages.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine connection
engine = create_engine(sqlite_url, echo=False)


# ==========================================
# 1. DATABASE MODEL
# ==========================================
class MessageLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    contact_name: str
    phone_number: str
    message: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = Field(default="SENT")


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def create_db_and_tables():
    """Creates the SQLite database and MessageLog table if they don't exist."""
    SQLModel.metadata.create_all(engine)


def log_message(contact_name: str, phone_number: str, message: str, status: str = "SENT"):
    """Inserts a new message record into the database."""
    with Session(engine) as session:
        log_entry = MessageLog(
            contact_name=contact_name,
            phone_number=phone_number,
            message=message,
            status=status,
        )
        session.add(log_entry)
        session.commit()
