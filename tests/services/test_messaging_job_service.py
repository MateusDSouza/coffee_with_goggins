from unittest.mock import MagicMock, patch

import pytest

from src.models.contact import Contact
from src.services.messaging_job_service import MessagingJobService


class TestMessagingJobService:
    """Isolated unit tests for the central orchestration service."""

    @pytest.fixture
    def mock_dependencies(self) -> dict[str, MagicMock]:
        """Provides a dictionary of mocked interfaces."""
        return {
            "llm": MagicMock(),
            "tts": MagicMock(),
            "messenger": MagicMock(),
            "repo": MagicMock(),
            "contact_repo": MagicMock(),
        }

    @pytest.fixture
    def service(self, mock_dependencies: dict[str, MagicMock]) -> MessagingJobService:
        """Injects the mocked dependencies into the service instance."""

        mock_dependencies["contact_repo"].get_contacts.return_value = [
            Contact(name="Maksin", phone_number="+34627463091")
        ]
        mock_dependencies["llm"].generate_message.return_value = "Hello from AI!"
        mock_dependencies["tts"].generate_audio.return_value = "/tmp/audio.mp3"

        return MessagingJobService(**mock_dependencies)

    @patch("src.services.messaging_job_service.time.sleep")
    def test_run_job_happy_path_sends_audio(
        self, mock_sleep: MagicMock, mock_dependencies: dict[str, MagicMock], service: MessagingJobService
    ) -> None:
        """Verifies the primary workflow where text generation, TTS, and sending all succeed."""

        # Act
        service.run_job()

        # Assert against the mock_dependencies dictionary to satisfy Mypy
        mock_dependencies["llm"].generate_message.assert_called_once_with("Maksin")
        mock_dependencies["tts"].generate_audio.assert_called_once_with("Hello from AI!", "Maksin")
        mock_dependencies["messenger"].send_audio.assert_called_once_with("+34627463091", "/tmp/audio.mp3")

        mock_dependencies["messenger"].send_message.assert_not_called()

        mock_dependencies["repo"].log_message.assert_called_once_with(
            "Maksin", "+34627463091", "AUDIO: /tmp/audio.mp3", "SENT"
        )
        mock_sleep.assert_called_once_with(3)

    @patch("src.services.messaging_job_service.time.sleep")
    def test_run_job_tts_fails_falls_back_to_text(
        self, mock_sleep: MagicMock, mock_dependencies: dict[str, MagicMock], service: MessagingJobService
    ) -> None:
        """Ensures that a TTS exception triggers the plain text dispatch fallback."""

        # Arrange
        mock_dependencies["tts"].generate_audio.side_effect = Exception("402 Payment Required")

        # Act
        service.run_job()

        # Assert
        mock_dependencies["messenger"].send_audio.assert_not_called()
        mock_dependencies["messenger"].send_message.assert_called_once_with("+34627463091", "Hello from AI!")
        mock_dependencies["repo"].log_message.assert_called_once_with(
            "Maksin", "+34627463091", "Hello from AI!", "SENT_TEXT_FALLBACK"
        )

    @patch("src.services.messaging_job_service.time.sleep")
    def test_run_job_logs_failure_if_fallback_fails(
        self, mock_sleep: MagicMock, mock_dependencies: dict[str, MagicMock], service: MessagingJobService
    ) -> None:
        """Verifies that if even the fallback text fails to send, a FAILED status is logged."""

        # Arrange
        mock_dependencies["tts"].generate_audio.side_effect = Exception("API Down")
        mock_dependencies["messenger"].send_message.side_effect = Exception("Browser Crashed")

        # Act
        service.run_job()

        # Assert
        mock_dependencies["repo"].log_message.assert_called_once_with(
            "Maksin", "+34627463091", "Hello from AI!", "FAILED"
        )

    @patch.object(MessagingJobService, "run_job")
    def test_run_once_calls_run_job(self, mock_run_job: MagicMock, service: MessagingJobService) -> None:
        """Verifies the run_once wrapper invokes the core logic exactly one time."""
        # Act
        service.run_once()

        # Assert
        mock_run_job.assert_called_once()

    @patch.object(MessagingJobService, "run_job")
    @patch("src.services.messaging_job_service.schedule")
    @patch("src.services.messaging_job_service.time.sleep", side_effect=KeyboardInterrupt)
    def test_start_scheduler_configures_and_runs(
        self, mock_sleep: MagicMock, mock_schedule: MagicMock, mock_run_job: MagicMock, service: MessagingJobService
    ) -> None:
        """Verifies the scheduler is set up properly and handles a graceful shutdown."""
        # Act
        service.start_scheduler(interval_minutes=5)

        # Assert
        mock_schedule.every.assert_called_once_with(5)
        mock_run_job.assert_called_once()
        mock_schedule.run_pending.assert_called_once()
