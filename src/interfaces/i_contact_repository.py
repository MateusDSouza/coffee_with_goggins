from abc import ABC, abstractmethod

from src.models.contact import Contact


class IContactRepository(ABC):
    @abstractmethod
    def get_contacts(self) -> list[Contact]:
        pass
