import time

import schedule

from src.interfaces.i_contact_repository import IContactRepository
from src.interfaces.i_llm_client import ILLMClient
from src.interfaces.i_message_repository import IMessageRepository
from src.interfaces.i_messenger_client import IMessengerClient
from src.interfaces.i_text_to_speech_client import ITextToSpeechClient


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
        print("\n--- 🚀 Starting Messaging Job ---")
        contacts = self.contact_repo.get_contacts()

        for contact in contacts:
            print(f"🧠 Generating text for {contact.name}...")
            text_message = self.llm.generate_message(contact.name)

            print("🎙️ Attempting audio conversion via Fish Audio...")
            try:
                # 1. Try to generate and send audio
                audio_path = self.tts.generate_audio(text_message, contact.name)
                self.messenger.send_audio(contact.phone_number, audio_path)
                self.repo.log_message(contact.name, contact.phone_number, f"AUDIO: {audio_path}", "SENT")
                print("💾 Saved audio message record to database!")

            except Exception as tts_error:
                # 2. If audio fails, fallback to plain text
                print(f"❌ Audio generation failed for {contact.name}: {tts_error}")
                print("⚠️ Falling back to standard text message...")

                try:
                    self.messenger.send_message(contact.phone_number, text_message)
                    self.repo.log_message(contact.name, contact.phone_number, text_message, "SENT_TEXT_FALLBACK")
                    print("💾 Saved fallback text record to database!")
                except Exception as messenger_error:
                    print(f"❌ Fatal error sending text fallback: {messenger_error}")
                    self.repo.log_message(contact.name, contact.phone_number, text_message, "FAILED")

            time.sleep(3)

    def run_once(self) -> None:
        """Executes the messaging job a single time and safely terminates."""
        print("▶️ Executing single-run messaging job...")
        self.run_job()
        print("✅ Job complete. Exiting gracefully.")

    def start_scheduler(self, interval_minutes: int = 2) -> None:
        """Sets up an infinite loop to run the job at specified intervals."""
        print(f"📅 Setting up the schedule to run every {interval_minutes} minutes...")
        schedule.every(interval_minutes).minutes.do(self.run_job)

        self.run_job()

        print("⏳ Scheduler is running. Keep this terminal open!")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Scheduler interrupted by user. Shutting down gracefully.")
