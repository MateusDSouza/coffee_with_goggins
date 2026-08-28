from abc import ABC, abstractmethod


class ILLMClient(ABC):
    @abstractmethod
    def generate_message(self, contact_name: str) -> str:
        pass
