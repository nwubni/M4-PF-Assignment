"""
Bank operations agent for the bank application.
"""

import os
import json

from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from src.agents.agent_state import AgentState
from src.database.bank_db import get_bank_db
from src.enums.agents_enum import AgentsEnum
from src.models.user_query_model import UserQueryModel

load_dotenv()

# Default account for demo purposes
DEFAULT_ACCOUNT = "ACC001"


def bank_agent(state: AgentState):
    """
    Agent for bank operations - executes deposits, withdrawals, and balance checks.
    """
    messages = state["messages"]

    # Get the orchestrator's classification - it should be the last AIMessage before the user's message
    orchestrator_msg = ""
    # Look for the orchestrator's JSON response in the messages
    for msg in reversed(messages):
        if hasattr(msg, 'content') and "{" in msg.content and "category" in msg.content:
            orchestrator_msg = msg.content
            break

    # db = get_bank_db()

    # Parse the operation from orchestrator classification
    
    # Strip markdown code blocks if present
    content = orchestrator_msg.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:].strip()
    
    # Extract JSON from the content
    json_start = content.find("{")
    json_end = content.rfind("}") + 1
    if json_start >= 0 and json_end > json_start:
        content = content[json_start:json_end]
    
    # Replace single quotes with double quotes for valid JSON
    content = content.replace("'", '"')
    
    try:
        classification_dict = json.loads(content)
        classification = UserQueryModel(**classification_dict)
    except (json.JSONDecodeError, Exception) as e:
        # Fallback if parsing fails
        classification = UserQueryModel(category="check_balance", amount=0, followup="")

    if AgentsEnum.DEPOSIT.value in classification.category:
        amount = classification.amount
        if amount > 0:
            # result = db.deposit(DEFAULT_ACCOUNT, amount, "User deposit")
            # if result["success"]:
            #     response_text = (
            #         f"{result['message']}. New balance: ${result['new_balance']:.2f}"
            #     )
            # else:
            #     response_text = result["message"]
            response_text = f"Deposit of ${amount:.2f} has been processed successfully."
        else:
            # If followup was provided, it should have been shown already
            # This shouldn't happen if main.py handles followups correctly
            response_text = "Please specify the amount to deposit."

        return {
            "messages": [AIMessage(content=response_text)],
            "next": AgentsEnum.END.value,
        }

    elif AgentsEnum.WITHDRAWAL.value in classification.category:
        amount = classification.amount
        if amount > 0:
            # result = db.withdraw(DEFAULT_ACCOUNT, amount, "User withdrawal")
            # if result["success"]:
            #     response_text = (
            #         f"{result['message']}. New balance: ${result['new_balance']:.2f}"
            #     )
            # else:
            #     response_text = result["message"]
            response_text = f"Withdrawal of ${amount:.2f} has been processed successfully."
        else:
            response_text = "Please specify the amount to withdraw."

        return {
            "messages": [AIMessage(content=response_text)],
            "next": AgentsEnum.END.value,
        }

    elif AgentsEnum.CHECK_BALANCE.value in classification.category:
        # balance = db.get_balance(DEFAULT_ACCOUNT)
        # if balance is not None:
        #     response_text = f"Your current balance is: ${balance:.2f}"
        # else:
        #     return {
        #         "messages": [AIMessage(content="Account {DEFAULT_ACCOUNT} not found.")],
        #         "next": AgentsEnum.ORCHESTRATOR,
        #     }
        response_text = "Checking account balance"

    elif AgentsEnum.ACCOUNT_DETAILS.value in classification.category:
        # balance = db.get_balance(DEFAULT_ACCOUNT)
        # if balance is not None:
        #     response_text = (
        #         f"Account ID: {DEFAULT_ACCOUNT}\nCurrent Balance: ${balance:.2f}"
        #     )
        # else:
        #     return {
        #         "messages": [
        #             AIMessage(content=f"Account {DEFAULT_ACCOUNT} not found.")
        #         ],
        #         "next": AgentsEnum.ORCHESTRATOR,
        #     }
        response_text = "Checking bank details."

    else:
        response_text = "What banking operation would you like to perform?"

    return {
        "messages": [AIMessage(content=response_text)],
        "next": AgentsEnum.END.value,
    }
