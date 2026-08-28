import logging
import time

import schedule

from src.interfaces.i_contact_repository import IContactRepository
from src.interfaces.i_llm_client import ILLMClient
from src.interfaces.i_message_repository import IMessageRepository
from src.interfaces.i_messenger_client import IMessengerClient
from src.interfaces.i_text_to_speech_client import ITextToSpeechClient

logger = logging.getLogger(__name__)


class MessagingJobService:
    """Coordinates message generation, audio conversion, sending, and logging."""

    def __init__(
        self,
        llm: ILLMClient,
        tts: ITextToSpeechClient,
        messenger: IMessengerClient,
        repo: IMessageRepository,
        contact_repo: IContactRepository,
    ) -> None:
        self.llm = llm
        self.tts = tts
        self.messenger = messenger
        self.repo = repo
        self.contact_repo = contact_repo

    def run_job(self) -> None:
        logger.info("Starting messaging job")
        contacts = self.contact_repo.get_contacts()

        for contact in contacts:
            logger.info(f"Generating text for contact: {contact.name}")
            text_message = self.llm.generate_message(contact.name)

            logger.info(f"Attempting audio conversion via TTS for contact: {contact.name}")
            try:
                # 1. Try to generate and send audio
                audio_path = self.tts.generate_audio(text_message, contact.name)
                self.messenger.send_audio(contact.phone_number, audio_path)
                self.repo.log_message(contact.name, contact.phone_number, f"AUDIO: {audio_path}", "SENT")
                logger.info(f"Saved audio message record to database for {contact.name}")

            except Exception as tts_error:
                # 2. If audio fails, fallback to plain text
                logger.error(f"Audio generation failed for {contact.name}: {tts_error}", exc_info=True)
                logger.warning(f"Falling back to standard text message for {contact.name}")

                try:
                    self.messenger.send_message(contact.phone_number, text_message)
                    self.repo.log_message(contact.name, contact.phone_number, text_message, "SENT_TEXT_FALLBACK")
                    logger.info(f"Saved fallback text record to database for {contact.name}")
                except Exception as messenger_error:
                    logger.error(
                        f"Fatal error sending text fallback for {contact.name}: {messenger_error}", exc_info=True
                    )
                    self.repo.log_message(contact.name, contact.phone_number, text_message, "FAILED")

            time.sleep(3)

    def run_once(self) -> None:
        """Executes the messaging job a single time and safely terminates."""
        logger.info("Executing single-run messaging job")
        self.run_job()
        logger.info("Job complete. Exiting gracefully.")

    def start_scheduler(self, interval_minutes: int = 2) -> None:
        """Sets up an infinite loop to run the job at specified intervals."""
        logger.info(f"Setting up schedule to run every {interval_minutes} minutes")
        schedule.every(interval_minutes).minutes.do(self.run_job)

        self.run_job()

        logger.info("Scheduler is running")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user. Shutting down gracefully.")
