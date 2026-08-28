import json
from pathlib import Path

from src.interfaces.i_contact_repository import IContactRepository
from src.models.contact import Contact


class JSONContactRepository(IContactRepository):
    """Loads contacts from a local JSON file to keep PII out of version control."""

    def __init__(self, file_path: str | Path = "contacts.json") -> None:
        self.file_path = Path(file_path)

    def get_contacts(self) -> list[Contact]:
        """Reads the JSON file and returns a list of Contact domain objects."""
        if not self.file_path.exists():
            print(f"⚠️ Warning: Contacts file '{self.file_path}' not found. Returning empty list.")
            return []

        with open(self.file_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
                return [Contact(name=item["name"], phone_number=item["phone_number"]) for item in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Error parsing '{self.file_path}': {e}")
                return []
