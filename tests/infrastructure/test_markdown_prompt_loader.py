from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.infrastructure.markdown_prompt_loader import MarkdownPromptLoader
from src.models.prompt_config import PromptConfig


class TestMarkdownPromptLoader:
    """Isolated unit tests for the Markdown configuration parser."""

    def test_load_parses_sections_correctly(self) -> None:
        """Verifies the happy path where headers cleanly divide the text into the PromptConfig."""
        # Arrange
        mock_md_content = (
            "# System Instruction\n"
            "You are a helpful AI.\n"
            "Always be polite.\n\n"
            "# User Prompt\n"
            "Hello {contact_name}!\n"
            "How are you today?"
        )
        expected_system = "You are a helpful AI.\nAlways be polite."
        expected_user = "Hello {contact_name}!\nHow are you today?"

        # Act
        with patch("src.infrastructure.markdown_prompt_loader.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_md_content)) as mocked_file:
                config = MarkdownPromptLoader.load("dummy_prompts.md")

        # Assert
        assert isinstance(config, PromptConfig)
        assert config.system_instruction == expected_system
        assert config.user_prompt_template == expected_user

        # Verify file operations
        mocked_file.assert_called_once_with(Path("dummy_prompts.md"), encoding="utf-8")

    def test_load_raises_error_if_file_missing(self) -> None:
        """Ensures the application fails fast if the markdown file does not exist."""
        with patch("src.infrastructure.markdown_prompt_loader.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Prompt file not found: missing.md"):
                MarkdownPromptLoader.load("missing.md")

    def test_load_ignores_text_before_headers(self) -> None:
        """Tests that any preamble text before the first valid header is safely ignored."""
        # Arrange
        mock_md_content = (
            "This is a random comment that should be ignored.\n" "# System\n" "System text.\n" "# User\n" "User text.\n"
        )

        # Act
        with patch("src.infrastructure.markdown_prompt_loader.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_md_content)):
                config = MarkdownPromptLoader.load("dummy.md")

        # Assert
        assert config.system_instruction == "System text."
        assert config.user_prompt_template == "User text."

    @pytest.mark.parametrize(
        "markdown_content",
        [
            # Test case insensitivity and extra whitespace in headers
            ("  # SYSTEM \n" "System text.\n" "# user configuration \n" "User text.\n"),
            # Test headers without extra trailing words
            ("# system\n" "System text.\n" "# user\n" "User text.\n"),
        ],
    )
    def test_load_handles_header_formatting_variations(self, markdown_content: str) -> None:
        """Verifies the parser's robustness against casing and whitespace variations in headers."""
        # Act
        with patch("src.infrastructure.markdown_prompt_loader.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=markdown_content)):
                config = MarkdownPromptLoader.load("dummy.md")

        # Assert
        assert config.system_instruction == "System text."
        assert config.user_prompt_template == "User text."
