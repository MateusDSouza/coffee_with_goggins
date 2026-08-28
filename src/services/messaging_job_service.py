import time

import schedule

from interfaces.i_contact_repository import IContactRepository
from interfaces.i_llm_client import ILLMClient
from interfaces.i_message_repository import IMessageRepository
from interfaces.i_messenger_client import IMessengerClient


class MessagingJobService:
    """Coordinates message generation, sending, and logging using injected dependencies."""

    def __init__(
        self, llm: ILLMClient, messenger: IMessengerClient, repo: IMessageRepository, contact_repo: IContactRepository
    ):
        self.llm = llm
        self.messenger = messenger
        self.repo = repo
        self.contact_repo = contact_repo

    def run_job(self) -> None:
        print("\n--- 🚀 Starting Scheduled Messaging Job ---")
        contacts = self.contact_repo.get_contacts()

        for contact in contacts:
            print(f"🧠 Generating message for {contact.name}...")
            message = self.llm.generate_message(contact.name)

            try:
                self.messenger.send_message(contact.phone_number, message)
                self.repo.log_message(contact.name, contact.phone_number, message, "SENT")
                print("💾 Saved message record to database!")
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                self.repo.log_message(contact.name, contact.phone_number, message, "FAILED")

            time.sleep(3)

    def start_scheduler(self, interval_minutes: int = 2) -> None:
        print("📅 Setting up the schedule...")
        schedule.every(interval_minutes).minutes.do(self.run_job)
        self.run_job()

        print("⏳ Scheduler is running. Keep this terminal open!")
        while True:
            schedule.run_pending()
            time.sleep(1)
