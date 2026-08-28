from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.ollama_client import OllamaClient
from src.models.prompt_config import PromptConfig


class TestOllamaClient:
    """Isolated unit tests for the Ollama LLM integration."""

    @pytest.fixture
    def prompt_config(self) -> PromptConfig:
        """Provides a reusable, deterministic prompt configuration."""
        return PromptConfig(
            system_instruction="You are a helpful assistant.",
            user_prompt_template="Say a warm hello to {contact_name}.",
        )

    @patch("src.infrastructure.ollama_client.Client")
    def test_generate_message_formats_prompts_and_parses_response(
        self, mock_client_class: MagicMock, prompt_config: PromptConfig
    ) -> None:
        """Verifies payload construction, prompt formatting, and response extraction."""
        # Arrange
        mock_client_instance = mock_client_class.return_value

        # Simulate the expected nested dictionary response from the Ollama SDK
        mock_client_instance.chat.return_value = {
            "model": "test-model",
            "message": {"role": "assistant", "content": "Hello Maksin! Have a wonderful day."},
        }

        client = OllamaClient(prompt_config=prompt_config, host="http://fake-host", model_name="test-model")

        # Act
        result = client.generate_message("Maksin")

        # Assert
        assert result == "Hello Maksin! Have a wonderful day."

        # Verify the client passed the exact correct structure to the SDK
        mock_client_instance.chat.assert_called_once_with(
            model="test-model",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say a warm hello to Maksin."},
            ],
        )

    @patch("src.infrastructure.ollama_client.Client")
    def test_generate_message_handles_missing_keys_gracefully(
        self, mock_client_class: MagicMock, prompt_config: PromptConfig
    ) -> None:
        """Ensures standard Python exceptions bubble up if the API response is malformed."""
        # Arrange
        mock_client_instance = mock_client_class.return_value

        # Simulate a malformed response missing the 'content' key
        mock_client_instance.chat.return_value = {"message": {}}

        client = OllamaClient(prompt_config=prompt_config)

        # Act & Assert
        with pytest.raises(KeyError):
            client.generate_message("Maksin")
