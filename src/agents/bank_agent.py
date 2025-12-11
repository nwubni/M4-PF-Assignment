"""
Bank operations agent for the bank application.
"""

import json
import re

from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from src.agents.agent_state import AgentState
from src.database.bank_db import get_bank_db
from src.enums.agents_enum import AgentsEnum
from src.enums.bank_operations_enum import BankOperationsEnum
from src.models.user_query_model import UserQueryModel

load_dotenv()

# Default account for demo purposes
DEFAULT_ACCOUNT = "ACC001"
db = get_bank_db()


def bank_agent(state: AgentState):
    """
    Agent for bank operations - executes deposits, withdrawals, and balance checks.
    """
    messages = state["messages"]

    # Get the user query (could be a sub-query in multi-query scenarios)
    user_query = None
    for msg in reversed(messages):
        if hasattr(msg, "content") and not isinstance(msg, AIMessage):
            user_query = msg.content
            break

    if not user_query:
        user_query = messages[0].content if messages else ""

    # Check if we're in multi-query mode
    result = state.get("result", {})
    is_multi_query = result.get("is_multi_query", False)

    # In multi-query mode, infer operation from the sub-query text
    # In single-query mode, parse from orchestrator's JSON classification
    classification = None

    if is_multi_query:
        # Infer operation from query text
        user_query_lower = user_query.lower()

        # Check for withdrawal first (before balance, since "remove" might not contain "balance")
        if any(
            word in user_query_lower
            for word in ["withdraw", "withdrawal", "remove", "take out"]
        ):
            numbers = re.findall(r"\d+\.?\d*", user_query)
            amount = float(numbers[0]) if numbers else 0
            classification = UserQueryModel(
                category=BankOperationsEnum.WITHDRAWAL, amount=amount, followup=""
            )
        elif (
            "deposit" in user_query_lower
            or "add" in user_query_lower
            or "put" in user_query_lower
        ):
            # Extract amount from query
            numbers = re.findall(r"\d+\.?\d*", user_query)
            amount = float(numbers[0]) if numbers else 0
            classification = UserQueryModel(
                category=BankOperationsEnum.DEPOSIT, amount=amount, followup=""
            )
        elif "balance" in user_query_lower or "account balance" in user_query_lower:
            classification = UserQueryModel(
                category=BankOperationsEnum.BALANCE, amount=0, followup=""
            )
        elif (
            "account details" in user_query_lower or "account info" in user_query_lower
        ):
            classification = UserQueryModel(
                category=BankOperationsEnum.ACCOUNT_DETAILS, amount=0, followup=""
            )
        else:
            classification = UserQueryModel(
                category=BankOperationsEnum.BALANCE, amount=0, followup=""
            )
    else:
        # Single query mode - look for orchestrator's JSON classification
        orchestrator_msg = ""
        for msg in reversed(messages):
            if (
                hasattr(msg, "content")
                and "{" in msg.content
                and "category" in msg.content
            ):
                orchestrator_msg = msg.content
                break

        if orchestrator_msg:
            # Strip markdown code blocks if present
            content = orchestrator_msg.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:].strip()

            # Replace single quotes with double quotes for valid JSON
            content = content.replace("'", '"')

            try:
                classification_dict = json.loads(content)
                classification = UserQueryModel(**classification_dict)
            except (json.JSONDecodeError, Exception) as e:
                classification = None

    # If no classification found, infer from user query (for multi-query scenarios)
    if not classification:
        user_query_lower = user_query.lower()
        if (
            BankOperationsEnum.BALANCE.value in user_query_lower
            or "account balance" in user_query_lower
        ):
            classification = UserQueryModel(
                category=BankOperationsEnum.BALANCE, amount=0, followup=""
            )
        elif BankOperationsEnum.DEPOSIT.value in user_query_lower:
            classification = UserQueryModel(
                category=BankOperationsEnum.DEPOSIT, amount=0, followup=""
            )
        elif BankOperationsEnum.WITHDRAWAL.value in user_query_lower:
            classification = UserQueryModel(
                category=BankOperationsEnum.WITHDRAWAL, amount=0, followup=""
            )
        else:
            # Default to check balance
            classification = UserQueryModel(
                category=BankOperationsEnum.BALANCE, amount=0, followup=""
            )

    if BankOperationsEnum.DEPOSIT.value in classification.category:
        amount = classification.amount
        if amount > 0:
            result = db.deposit(DEFAULT_ACCOUNT, amount, "User deposit")
            if result["success"]:
                response_text = f"${amount:.2f} successfully deposited."
            else:
                response_text = result["message"]
        else:
            # If followup was provided, it should have been shown already
            response_text = "Please specify the amount to deposit."

    elif BankOperationsEnum.WITHDRAWAL.value in classification.category:
        amount = classification.amount
        if amount > 0:
            result = db.withdraw(DEFAULT_ACCOUNT, amount, "User withdrawal")
            if result["success"]:
                response_text = f"${amount:.2f} successfully withdrawn."
            else:
                response_text = result["message"]
        else:
            response_text = "Please specify the amount to withdraw."

    elif BankOperationsEnum.BALANCE.value in classification.category:
        result = db.get_balance(DEFAULT_ACCOUNT)
        if result is not None:
            response_text = f"Your current account balance is ${result:.2f}."
        else:
            response_text = "Sorry, I couldn't retrieve your balance at the moment."

    elif BankOperationsEnum.ACCOUNT_DETAILS.value in classification.category:
        result = db.get_account_details(DEFAULT_ACCOUNT)
        if result:
            response_text = f"Account ID: {result['account_id']}\nAccount Type: {result['account_type']}\nCurrent Balance: ${result['balance']:.2f}"
        else:
            response_text = (
                "Sorry, I couldn't retrieve your account details at the moment."
            )

    else:
        response_text = "What banking operation would you like to perform?"

    # Check if this is part of a multi-query
    result = state.get("result", {})
    if result.get("is_multi_query"):
        # In multi-query, return only the response and route back to orchestrator
        # The orchestrator will manage message history
        return {
            "messages": [AIMessage(content=response_text)],
            "next": AgentsEnum.ORCHESTRATOR.value,
            "result": result,
        }
    else:
        # Single query, end here
        return {
            "messages": [AIMessage(content=response_text)],
            "next": AgentsEnum.END.value,
        }
