# job/routine.py
import time

import schedule

from db.database import log_message  # <-- Import database logger
from llm.llm_client import generate_message, get_ai_client
from whatsapp.whatsapp_client import send_whatsapp_message


def get_contacts():
    return []


def messaging_job():
    print("\n--- 🚀 Starting Scheduled Messaging Job ---")

    client, model = get_ai_client(provider="ollama")
    contacts = get_contacts()

    for contact in contacts:
        print(f"🧠 Generating message for {contact['name']}...")
        message = generate_message(client, model, contact["name"])

        print(f"✅ Message ready:\n{message}")

        try:
            # Send via pywhatkit
            send_whatsapp_message(contact["number"], message)

            # Log successful send to database
            log_message(
                contact_name=contact["name"],
                phone_number=contact["number"],
                message=message,
                status="SENT",
            )
            print("💾 Saved message record to database!")

        except Exception as e:
            print(f"❌ Error sending message: {e}")
            # Log failure to database
            log_message(
                contact_name=contact["name"],
                phone_number=contact["number"],
                message=message,
                status="FAILED",
            )

        time.sleep(3)


def start_scheduler():
    print("📅 Setting up the schedule...")
    schedule.every(2).minutes.do(messaging_job)

    messaging_job()

    print("⏳ Scheduler is running. Keep this terminal open!")

    while True:
        schedule.run_pending()
        time.sleep(1)
