"""
Bank operations agent for the bank application.
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from src.enums.agents_enum import AgentsEnum
from src.models.user_query_model import UserQueryModel
from src.agents.agent_state import AgentState
from src.database.bank_db import get_bank_db

load_dotenv()

# Default account for demo purposes
DEFAULT_ACCOUNT = "ACC001"


def bank_agent(state: AgentState):
    """
    Agent for bank operations - executes deposits, withdrawals, and balance checks.
    """
    messages = state["messages"]

    # Get the orchestrator's classification from the last message
    orchestrator_msg = messages[-1].content if len(messages) > 1 else ""

    db = get_bank_db()

    # Parse the operation from orchestrator classification
    classification = UserQueryModel(**orchestrator_msg)

    if "deposit" in classification.category:
        amount = classification.amount
        if amount > 0:
            result = db.deposit(DEFAULT_ACCOUNT, amount, "User deposit")
            if result["success"]:
                response_text = (
                    f"{result['message']}. New balance: ${result['new_balance']:.2f}"
                )
            else:
                response_text = result["message"]
        else:
            return {
                "messages": [
                    AIMessage(content="Please specify the amount to deposit.")
                ],
                "next": AgentsEnum.ORCHESTRATOR,
            }

    elif "withdrawal" in classification.category:
        amount = classification.amount
        if amount > 0:
            result = db.withdraw(DEFAULT_ACCOUNT, amount, "User withdrawal")
            if result["success"]:
                response_text = (
                    f"{result['message']}. New balance: ${result['new_balance']:.2f}"
                )
            else:
                response_text = result["message"]
        else:
            return {
                "messages": [
                    AIMessage(content="Please specify the amount to withdraw.")
                ],
                "next": AgentsEnum.ORCHESTRATOR,
            }

    elif "check_balance" in classification.category:
        balance = db.get_balance(DEFAULT_ACCOUNT)
        if balance is not None:
            response_text = f"Your current balance is: ${balance:.2f}"
        else:
            return {
                "messages": [AIMessage(content="Account {DEFAULT_ACCOUNT} not found.")],
                "next": AgentsEnum.ORCHESTRATOR,
            }

    elif "account_details" in classification.category:
        balance = db.get_balance(DEFAULT_ACCOUNT)
        if balance is not None:
            response_text = (
                f"Account ID: {DEFAULT_ACCOUNT}\nCurrent Balance: ${balance:.2f}"
            )
        else:
            return {
                "messages": [
                    AIMessage(content=f"Account {DEFAULT_ACCOUNT} not found.")
                ],
                "next": AgentsEnum.ORCHESTRATOR,
            }

    else:
        response_text = "What banking operation would you like to perform?"

    return {
        "messages": [AIMessage(content=response_text)],
        "next": "END",
    }
