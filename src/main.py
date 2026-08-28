from pathlib import Path

from src.infrastructure.json_contact_repository import JSONContactRepository
from src.infrastructure.markdown_prompt_loader import MarkdownPromptLoader
from src.infrastructure.ollama_client import OllamaClient
from src.infrastructure.sqlite_message_repository import SQLiteMessageRepository
from src.infrastructure.whatsapp_messenger import WhatsAppMessenger
from src.services import MessagingJobService


def main() -> None:
    print("⚙️ Booting up HoLLyM Agent...")

    prompt_file_path = Path(__file__).parent.parent / "prompts" / "hollym.md"
    prompt_config = MarkdownPromptLoader.load(prompt_file_path)

    llm_client = OllamaClient(prompt_config=prompt_config)
    db_repo = SQLiteMessageRepository()
    messenger = WhatsAppMessenger()
    contact_repo = JSONContactRepository(file_path="contacts.json")

    bot_service = MessagingJobService(llm=llm_client, messenger=messenger, repo=db_repo, contact_repo=contact_repo)

    bot_service.start_scheduler(interval_minutes=2)


if __name__ == "__main__":
    main()
