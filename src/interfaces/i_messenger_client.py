from abc import ABC, abstractmethod


class IMessengerClient(ABC):
    @abstractmethod
    def send_message(self, phone_number: str, message: str) -> None:
        pass
