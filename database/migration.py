import os

from alembic import command
from alembic.config import Config


def run_migrations():
    alembic_ini_path = "alembic.ini"

    if not os.path.exists(alembic_ini_path):
        print("Error: alembic.ini file not found. Run 'alembic init alembic' first.")
        return

    alembic_cfg = Config(alembic_ini_path)

    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrated successfully.")
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
