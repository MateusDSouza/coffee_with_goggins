from unittest.mock import MagicMock, patch

import pytest

from src.main import main


class TestMainCompositionRoot:
    """Isolated unit tests for the application's Composition Root."""

    @patch("src.main.MessagingJobService")
    @patch("src.main.JSONContactRepository")
    @patch("src.main.WhatsAppMessenger")
    @patch("src.main.SQLiteMessageRepository")
    @patch("src.main.FishAudioTTSClient")
    @patch("src.main.OllamaClient")
    @patch("src.main.MarkdownPromptLoader.load")
    @patch("src.main.os.getenv")
    @patch("src.main.load_dotenv")
    def test_main_wires_dependencies_and_runs_successfully(
        self,
        mock_load_dotenv: MagicMock,
        mock_getenv: MagicMock,
        mock_prompt_loader: MagicMock,
        mock_ollama: MagicMock,
        mock_tts: MagicMock,
        mock_db: MagicMock,
        mock_messenger: MagicMock,
        mock_contact_repo: MagicMock,
        mock_job_service: MagicMock,
    ) -> None:
        """Verifies that all dependencies are instantiated and the service executes run_once()."""

        # Arrange - Mock the environment variables safely
        def mock_env_vars(key: str, default: str | None = None) -> str | None:
            if key == "FISH_AUDIO_API_KEY":
                return "fake_api_key"
            elif key == "FISH_AUDIO_VOICE_ID":
                return "fake_voice_id"
            elif key == "FISH_AUDIO_MODEL":
                return "s2.1-pro-free"
            elif key == "OLLAMA_HOST":
                return "http://localhost:11434"
            elif key == "OLLAMA_MODEL":
                return "dolphin-llama3"
            return default

        mock_getenv.side_effect = mock_env_vars
        mock_prompt_config = MagicMock()
        mock_prompt_loader.return_value = mock_prompt_config

        mock_service_instance = mock_job_service.return_value

        # Act
        main()

        # Assert - Verify environment was loaded
        mock_load_dotenv.assert_called_once()

        # Assert - Verify all dependencies were constructed correctly
        mock_prompt_loader.assert_called_once()
        mock_ollama.assert_called_once_with(
            prompt_config=mock_prompt_config,
            host="http://localhost:11434",
            model_name="dolphin-llama3",
        )
        mock_tts.assert_called_once_with(api_key="fake_api_key", voice_id="fake_voice_id", model="s2.1-pro-free")
        mock_db.assert_called_once()
        mock_messenger.assert_called_once()
        mock_contact_repo.assert_called_once_with(file_path="contacts.json")

        # Assert - Verify the service was injected with the mocked dependencies
        mock_job_service.assert_called_once_with(
            llm=mock_ollama.return_value,
            tts=mock_tts.return_value,
            messenger=mock_messenger.return_value,
            repo=mock_db.return_value,
            contact_repo=mock_contact_repo.return_value,
        )

        # Assert - Verify execution was triggered
        mock_service_instance.run_once.assert_called_once()

    @patch("src.main.os.getenv")
    @patch("src.main.load_dotenv")
    def test_main_raises_error_if_api_key_missing(self, mock_load_dotenv: MagicMock, mock_getenv: MagicMock) -> None:
        """Ensures the application fails fast before instantiating classes if critical secrets are missing."""

        # Arrange - Simulate a missing API key
        mock_getenv.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Critical Error: FISH_AUDIO_API_KEY is missing from the environment."):
            main()
