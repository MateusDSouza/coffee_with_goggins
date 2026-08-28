from abc import ABC, abstractmethod


class ITextToSpeechClient(ABC):
    """Abstract contract for text-to-speech generation."""

    @abstractmethod
    def generate_audio(self, text: str, contact_name: str) -> str:
        """Converts text to an audio file and returns the local file path."""
        pass
