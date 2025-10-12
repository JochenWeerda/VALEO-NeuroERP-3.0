"""
Utility script to initialize the database schema without starting the full FastAPI server.
"""

from app.core.database import create_tables


def main() -> None:
    create_tables()
    print("Database schema initialized.")


if __name__ == "__main__":
    main()
