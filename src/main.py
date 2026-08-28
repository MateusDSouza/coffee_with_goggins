from db.database import create_db_and_tables
from job.routine import start_scheduler


def main():
    print("⚙️ Booting up HoLLyM Agent...")

    print("🗄️ Initializing SQLite database...")
    create_db_and_tables()

    start_scheduler()


if __name__ == "__main__":
    main()
