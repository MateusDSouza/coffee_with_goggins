from src.infrastructure.json_contact_repository import JSONContactRepository
from src.infrastructure.ollama_client import OllamaClient
from src.infrastructure.sqlite_message_repository import SQLiteMessageRepository
from src.infrastructure.whatsapp_messenger import WhatsAppMessenger
from src.services import MessagingJobService


def main() -> None:
    print("⚙️ Booting up HoLLyM Agent...")

    db_repo = SQLiteMessageRepository()
    llm_client = OllamaClient()
    messenger = WhatsAppMessenger()
    contact_repo = JSONContactRepository(file_path="contacts.json")

    bot_service = MessagingJobService(llm=llm_client, messenger=messenger, repo=db_repo, contact_repo=contact_repo)

    bot_service.start_scheduler(interval_minutes=2)


if __name__ == "__main__":
    main()
