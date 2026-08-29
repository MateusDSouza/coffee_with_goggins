import logging
import time

import schedule

from src.interfaces.i_audio_mixer import IAudioMixer
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
        audio_mixer: IAudioMixer,
        messenger: IMessengerClient,
        repo: IMessageRepository,
        contact_repo: IContactRepository,
    ) -> None:
        self.llm = llm
        self.tts = tts
        self.audio_mixer = audio_mixer
        self.messenger = messenger
        self.repo = repo
        self.contact_repo = contact_repo

    def run_job(self) -> None:
        logger.info("Starting messaging job")

        try:
            contacts = self.contact_repo.get_contacts()
        except Exception as repo_err:
            logger.error(f"Failed to fetch contacts from repository: {repo_err}", exc_info=True)
            return

        for contact in contacts:
            text_message: str | None = None

            # 1. Generate text script via LLM
            try:
                logger.info(f"Generating text for contact: {contact.name}")
                text_message = self.llm.generate_message(contact.name)
            except Exception as llm_err:
                logger.error(f"LLM text generation failed for contact {contact.name}: {llm_err}", exc_info=True)
                continue

            # 2. Process audio workflow (TTS + Audio Mixing + WhatsApp Dispatch)
            audio_sent = False
            try:
                logger.info(f"Attempting audio conversion via TTS for contact: {contact.name}")
                raw_audio_path = self.tts.generate_audio(text_message, contact.name)

                # Mix raw voice note with a random background track
                mixed_audio_path = raw_audio_path
                try:
                    logger.info(f"Mixing background music for contact: {contact.name}")
                    mixed_audio_path = self.audio_mixer.mix_with_random_background(raw_audio_path)
                except Exception as mixer_err:
                    logger.warning(
                        f"Audio mixing failed for {contact.name}: {mixer_err}. Falling back to unmixed voice track.",
                        exc_info=True,
                    )

                logger.info(f"Dispatching voice message to contact: {contact.name}")
                self.messenger.send_audio(contact.phone_number, mixed_audio_path)
                audio_sent = True

                # Log successful audio dispatch
                try:
                    self.repo.log_message(contact.name, contact.phone_number, text_message, "SENT")
                    logger.info(f"Saved audio message record to database for {contact.name}")
                except Exception as db_err:
                    logger.error(f"Failed to log SENT status to database for {contact.name}: {db_err}", exc_info=True)

            except Exception as audio_workflow_err:
                logger.error(f"Audio dispatch workflow failed for {contact.name}: {audio_workflow_err}", exc_info=True)

            # 3. Fallback to standard text message if audio dispatch failed
            if not audio_sent:
                logger.warning(f"Falling back to standard text message for {contact.name}")
                try:
                    self.messenger.send_message(contact.phone_number, text_message)
                    self.repo.log_message(contact.name, contact.phone_number, text_message, "SENT_TEXT_FALLBACK")
                    logger.info(f"Saved fallback text record to database for {contact.name}")
                except Exception as fallback_err:
                    logger.error(f"Fatal error sending text fallback for {contact.name}: {fallback_err}", exc_info=True)
                    try:
                        self.repo.log_message(contact.name, contact.phone_number, text_message, "FAILED")
                    except Exception as db_err:
                        logger.error(
                            f"Failed to log FAILED status to database for {contact.name}: {db_err}", exc_info=True
                        )

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
