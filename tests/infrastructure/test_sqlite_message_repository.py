import pytest
from sqlmodel import Session, select

from src.infrastructure.sqlite_message_repository import SQLiteMessageRepository
from src.models.message_log import MessageLog


class TestSQLiteMessageRepository:
    """Isolated unit tests for the SQLite repository using an in-memory database."""

    @pytest.fixture
    def in_memory_repo(self) -> SQLiteMessageRepository:
        """Provides a fresh, isolated repository instance running in memory."""
        # Using :memory: ensures tables are created in RAM and destroyed after the test
        return SQLiteMessageRepository(db_url="sqlite:///:memory:")

    def test_log_message_inserts_record_successfully(self, in_memory_repo: SQLiteMessageRepository) -> None:
        """Verifies that the repository correctly maps and saves all fields to the database."""
        # Act
        in_memory_repo.log_message(
            contact_name="Ivan", phone_number="+34648917313", message="God bless you!", status="FAILED"
        )

        # Assert: Open a direct session to verify the state of the database
        with Session(in_memory_repo.engine) as session:
            logs = session.exec(select(MessageLog)).all()

            assert len(logs) == 1
            log_entry = logs[0]

            assert log_entry.id is not None  # DB should have auto-assigned an ID
            assert log_entry.contact_name == "Ivan"
            assert log_entry.phone_number == "+34648917313"
            assert log_entry.message == "God bless you!"
            assert log_entry.status == "FAILED"
            assert log_entry.sent_at is not None

    def test_log_message_uses_default_status(self, in_memory_repo: SQLiteMessageRepository) -> None:
        """Ensures that omitting the status argument defaults to 'SENT'."""
        # Act
        in_memory_repo.log_message(contact_name="Maksin", phone_number="+34627463091", message="Morning!")

        # Assert
        with Session(in_memory_repo.engine) as session:
            log_entry = session.exec(select(MessageLog)).first()
            assert log_entry is not None
            assert log_entry.status == "SENT"
