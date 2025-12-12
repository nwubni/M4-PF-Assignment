"""
Simple SQLite database for banking operations.
"""

import sqlite3
import os
from datetime import datetime


class BankDB:
    """Simple banking database manager."""

    def __init__(self, db_path=None):
        """Initialize database connection."""
        if db_path is None:
            # Default to storage/database directory
            db_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "storage", "database"
            )
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "banking.db")
        else:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    account_name TEXT NOT NULL,
                    balance REAL DEFAULT 0.0
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
                )
            """
            )
            conn.commit()

    def get_balance(self, account_id: str) -> float:
        """Get account balance."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT balance FROM accounts WHERE account_id = ?", (account_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def deposit(self, account_id: str, amount: float, description: str = "") -> dict:
        """Deposit money into account."""
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}

        with sqlite3.connect(self.db_path) as conn:
            # Check if account exists
            cursor = conn.execute(
                "SELECT balance FROM accounts WHERE account_id = ?", (account_id,)
            )
            result = cursor.fetchone()

            if not result:
                return {"success": False, "message": f"Account {account_id} not found"}

            new_balance = result[0] + amount

            # Update balance
            conn.execute(
                "UPDATE accounts SET balance = ? WHERE account_id = ?",
                (new_balance, account_id),
            )

            # Record transaction
            conn.execute(
                """INSERT INTO transactions 
                   (account_id, transaction_type, amount, timestamp, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    account_id,
                    "deposit",
                    amount,
                    datetime.now().isoformat(),
                    description,
                ),
            )
            conn.commit()

            return {
                "success": True,
                "message": f"Deposited ${amount:.2f}",
                "new_balance": new_balance,
            }

    def withdraw(self, account_id: str, amount: float, description: str = "") -> dict:
        """Withdraw money from account."""
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT balance FROM accounts WHERE account_id = ?", (account_id,)
            )
            result = cursor.fetchone()

            if not result:
                return {"success": False, "message": f"Account {account_id} not found"}

            current_balance = result[0]

            if current_balance < amount:
                return {
                    "success": False,
                    "message": f"Insufficient funds. Current balance: ${current_balance:.2f}",
                }

            new_balance = current_balance - amount

            # Update balance
            conn.execute(
                "UPDATE accounts SET balance = ? WHERE account_id = ?",
                (new_balance, account_id),
            )

            # Record transaction
            conn.execute(
                """INSERT INTO transactions 
                   (account_id, transaction_type, amount, timestamp, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    account_id,
                    "withdrawal",
                    amount,
                    datetime.now().isoformat(),
                    description,
                ),
            )
            conn.commit()

            return {
                "success": True,
                "message": f"Withdrew ${amount:.2f}",
                "new_balance": new_balance,
            }

    def get_account_details(self, account_id: str) -> dict:
        """Get account details."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT account_id, account_name, balance FROM accounts WHERE account_id = ?",
                (account_id,),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "account_id": result[0],
                    "account_type": result[1],
                    "balance": result[2],
                }
            return None

    def get_transaction_history(self, account_id: str, limit: int = 5) -> list:
        """Get transaction history for an account."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT transaction_id, transaction_type, amount, timestamp, description
                   FROM transactions 
                   WHERE account_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (account_id, limit),
            )
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    "transaction_id": row[0],
                    "type": row[1],
                    "amount": row[2],
                    "timestamp": row[3],
                    "description": row[4] or ""
                })
            return transactions

    def create_account(
        self, account_id: str, account_name: str, initial_balance: float = 0.0
    ) -> dict:
        """Create a new account."""
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO accounts (account_id, account_name, balance) VALUES (?, ?, ?)",
                    (account_id, account_name, initial_balance),
                )
                conn.commit()
                return {
                    "success": True,
                    "message": f"Account {account_id} created successfully",
                }
            except sqlite3.IntegrityError:
                return {
                    "success": False,
                    "message": f"Account {account_id} already exists",
                }


# Singleton instance
_db_instance = None


def get_bank_db() -> BankDB:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = BankDB()
    return _db_instance
