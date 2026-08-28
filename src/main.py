import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from src.infrastructure.fish_audio_client import FishAudioTTSClient
from src.infrastructure.json_contact_repository import JSONContactRepository
from src.infrastructure.markdown_prompt_loader import MarkdownPromptLoader
from src.infrastructure.ollama_client import OllamaClient
from src.infrastructure.sqlite_message_repository import SQLiteMessageRepository
from src.infrastructure.whatsapp_messenger import WhatsAppMessenger
from src.services.messaging_job_service import MessagingJobService


def setup_logging() -> None:
    """Configures global logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("goggins_agent.log", encoding="utf-8"),
        ],
    )


def main() -> None:
    # 0. Initialize global logging configuration
    setup_logging()
    logger = logging.getLogger(__name__)

    # 1. Inject environment variables from .env into the system environment
    load_dotenv()

    logger.info("Booting up Goggins Agent")

    # 2. Safely retrieve the required secrets
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "dolphin-llama3")
    fish_api_key = os.getenv("FISH_AUDIO_API_KEY")
    fish_voice_id = os.getenv("FISH_AUDIO_VOICE_ID")
    fish_model = os.getenv("FISH_AUDIO_MODEL", "s2.1-pro-free")
    if not fish_api_key:
        logger.critical("Critical Error: FISH_AUDIO_API_KEY is missing from the environment.")
        raise ValueError("Critical Error: FISH_AUDIO_API_KEY is missing from the environment.")

    # 3. Load configurations
    prompt_file_path = Path(__file__).parent.parent / "prompts" / "goggins_agent.md"
    logger.debug(f"Loading prompt configuration from {prompt_file_path}")
    prompt_config = MarkdownPromptLoader.load(prompt_file_path)

    # 4. Initialize dependencies
    logger.debug("Initializing infrastructure dependencies")
    llm_client = OllamaClient(prompt_config=prompt_config, host=ollama_host, model_name=ollama_model)
    tts_client = FishAudioTTSClient(api_key=fish_api_key, voice_id=fish_voice_id, model=fish_model)
    db_repo = SQLiteMessageRepository()
    messenger = WhatsAppMessenger()
    contact_repo = JSONContactRepository(file_path="contacts.json")

    # 5. Wire the application
    logger.debug("Wiring MessagingJobService orchestration layer")
    bot_service = MessagingJobService(
        llm=llm_client, tts=tts_client, messenger=messenger, repo=db_repo, contact_repo=contact_repo
    )

    bot_service.run_once()


if __name__ == "__main__":
    main()
