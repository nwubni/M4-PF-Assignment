"""
Enum for agent names.
"""

from enum import Enum


class AgentsEnum(Enum):
    """
    Enum for agent names.
    """

    ORCHESTRATOR = "orchestrator"
    BANK = "bank"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    CHECK_BALANCE = "check_balance"
    ACCOUNT_DETAILS = "account_details"
    POLICY = "policy"
    FAQ = "faq"
    INVESTMENT = "investment"
    END = "END"
