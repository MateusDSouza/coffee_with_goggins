import json
from unittest.mock import mock_open, patch

import pytest

from src.infrastructure.json_contact_repository import JSONContactRepository
from src.models.contact import Contact


class TestJSONContactRepository:
    """Isolated unit tests for the JSON file-based contact repository."""

    def test_get_contacts_success(self) -> None:
        """Verifies that a well-formed JSON file correctly maps to Contact objects."""
        # Arrange
        valid_json_data = [
            {"name": "Maksin", "phone_number": "+34627463091"},
            {"name": "Ivan", "phone_number": "+34648917313"},
        ]
        mock_file_content = json.dumps(valid_json_data)
        repo = JSONContactRepository(file_path="dummy.json")

        # Act
        with patch("src.infrastructure.json_contact_repository.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_file_content)) as mocked_file:
                contacts = repo.get_contacts()

        # Assert
        assert len(contacts) == 2
        assert isinstance(contacts[0], Contact)
        assert contacts[0].name == "Maksin"
        assert contacts[0].phone_number == "+34627463091"
        assert contacts[1].name == "Ivan"

        # Verify the file was opened with the correct encoding
        mocked_file.assert_called_once_with(repo.file_path, encoding="utf-8")

    def test_get_contacts_returns_empty_if_file_missing(self) -> None:
        """Ensures that a missing file gracefully returns an empty list without crashing."""
        # Arrange
        repo = JSONContactRepository(file_path="missing.json")

        # Act
        with patch("src.infrastructure.json_contact_repository.Path.exists", return_value=False):
            with patch("builtins.open", mock_open()) as mocked_file:
                contacts = repo.get_contacts()

        # Assert
        assert contacts == []
        mocked_file.assert_not_called()

    @pytest.mark.parametrize(
        ("file_content", "error_description"),
        [
            ("this is not json", "JSONDecodeError"),
            ("[{}]", "Missing both keys"),
            ('[{"name": "Maksin"}]', "Missing phone_number key"),
            ('[{"phone_number": "+12345"}]', "Missing name key"),
        ],
    )
    def test_get_contacts_handles_parsing_errors(self, file_content: str, error_description: str) -> None:
        """Tests that malformed JSON or missing dictionary keys are caught and return an empty list."""
        # Arrange
        repo = JSONContactRepository(file_path="bad_data.json")

        # Act
        with patch("src.infrastructure.json_contact_repository.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=file_content)):
                contacts = repo.get_contacts()

        # Assert
        assert contacts == []
