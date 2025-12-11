"""
Bank operations enums.
"""

from enum import Enum


class BankOperationsEnum(Enum):
    """Enum for bank operations."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BALANCE = "balance"
    ACCOUNT_DETAILS = "account_details"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value
