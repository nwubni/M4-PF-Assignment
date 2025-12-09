"""
Initialize the banking database with demo data.
"""

from bank_db import get_bank_db


def init_database():
    """Create demo account with initial balance."""
    db = get_bank_db()

    # Create demo account
    result = db.create_account("ACC001", "Demo User", initial_balance=1000.0)
    print(result["message"])

    print("\nDatabase initialized successfully!")
    print("Demo Account: ACC001")
    print("Initial Balance: $1000.00")


if __name__ == "__main__":
    init_database()
