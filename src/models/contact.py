from dataclasses import dataclass


@dataclass
class Contact:
    """Domain model representing a target contact."""

    name: str
    phone_number: str
