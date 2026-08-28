from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from requests.exceptions import HTTPError

from src.infrastructure.fish_audio_client import FishAudioTTSClient


class TestFishAudioTTSClient:
    """Isolated unit tests for the Fish Audio HTTP client."""

    @patch("src.infrastructure.fish_audio_client.Path.mkdir")
    def test_init_creates_output_directory(self, mock_mkdir: MagicMock) -> None:
        """Ensures the output directory is created upon instantiation."""
        FishAudioTTSClient(api_key="fake", output_dir="custom_audio_dir")
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @pytest.mark.parametrize(
        ("voice_id", "expected_reference_id_in_payload"),
        [
            ("custom_voice_123", True),
            (None, False),
        ],
    )
    @patch("src.infrastructure.fish_audio_client.requests.post")
    def test_generate_audio_payload_construction(
        self, mock_post: MagicMock, voice_id: str | None, expected_reference_id_in_payload: bool
    ) -> None:
        """Verifies the JSON payload is constructed correctly based on the presence of a voice_id."""
        # Arrange
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk1"]
        mock_post.return_value = mock_response

        client = FishAudioTTSClient(api_key="fake_key", voice_id=voice_id)

        # Act
        with patch("builtins.open", mock_open()):
            client.generate_audio("Hello", "Maksin")

        # Assert
        called_args, called_kwargs = mock_post.call_args
        payload = called_kwargs["json"]

        assert payload["text"] == "Hello"
        assert payload["format"] == "mp3"

        if expected_reference_id_in_payload:
            assert payload["reference_id"] == "custom_voice_123"
        else:
            assert "reference_id" not in payload

    @patch("src.infrastructure.fish_audio_client.requests.post")
    def test_generate_audio_writes_stream_to_file(self, mock_post: MagicMock) -> None:
        """Ensures the HTTP stream is correctly written to the local disk in chunks."""
        # Arrange
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"audio", b"_data"]
        mock_post.return_value = mock_response

        client = FishAudioTTSClient(api_key="fake_key")

        # Act
        with patch("builtins.open", mock_open()) as mocked_file:
            result_path = client.generate_audio("Test text", "Maksin")

        # Assert
        assert result_path == "output_audio/message_Maksin.mp3"

        # FIX: Assert using a Path object, matching what the client actually passed to open()
        expected_path = Path("output_audio/message_Maksin.mp3")
        mocked_file.assert_called_once_with(expected_path, "wb")

        # Verify the chunks were written sequentially
        file_handle = mocked_file()
        assert file_handle.write.call_count == 2
        file_handle.write.assert_any_call(b"audio")
        file_handle.write.assert_any_call(b"_data")

    @patch("src.infrastructure.fish_audio_client.requests.post")
    def test_generate_audio_raises_for_status_on_http_error(self, mock_post: MagicMock) -> None:
        """Verifies that an HTTP error prevents file writing and bubbles up the exception."""
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("402 Payment Required")
        mock_post.return_value = mock_response

        client = FishAudioTTSClient(api_key="fake_key")

        # Act & Assert
        with patch("builtins.open", mock_open()) as mocked_file:
            with pytest.raises(HTTPError, match="402 Payment Required"):
                client.generate_audio("Fail test", "Maksin")

        # Ensure no file was opened or written to because the exception halted execution
        mocked_file.assert_not_called()
