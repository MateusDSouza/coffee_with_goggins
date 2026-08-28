from abc import ABC, abstractmethod


class IMessengerClient(ABC):
    @abstractmethod
    def send_message(self, phone_number: str, message: str) -> None:
        pass

    @abstractmethod
    def send_audio(self, phone_number: str, audio_file_path: str) -> None:
        """Sends an audio file to the specified phone number."""
        pass
