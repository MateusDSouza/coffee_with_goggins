from abc import ABC, abstractmethod


class IMessageRepository(ABC):
    @abstractmethod
    def log_message(self, contact_name: str, phone_number: str, message: str, status: str) -> None:
        pass
