from sqlmodel import Session, SQLModel, create_engine

from src.interfaces.i_message_repository import IMessageRepository
from src.models.message_log import MessageLog


class SQLiteMessageRepository(IMessageRepository):
    def __init__(self, db_url: str = "sqlite:///messages.db"):
        self.engine = create_engine(db_url, echo=False)
        SQLModel.metadata.create_all(self.engine)

    def log_message(self, contact_name: str, phone_number: str, message: str, status: str = "SENT") -> None:
        with Session(self.engine) as session:
            log_entry = MessageLog(
                contact_name=contact_name,
                phone_number=phone_number,
                message=message,
                status=status,
            )
            session.add(log_entry)
            session.commit()
