"""
Orchestrator class that classifies user queries into agent categories.
"""

import os
import sys
import json

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from langchain_openai import ChatOpenAI
from src.models.user_query_model import UserQueryModel
from src.agents.agent_state import AgentState
from src.utils.prompt_loader import load_prompt

# Add path for evaluator import
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


load_dotenv()


actions = {
    "bank": "bank_agent",
    "policy": "policy_agent",
    "faq": "faq_agent",
    "default": "default_agent",
}

# Map categories to agent names
category_mapping = {
    "deposit": "bank",
    "withdrawal": "bank",
    "check_balance": "bank",
    "account_details": "bank",
    "investment": "investment",
    "faq": "faq",
    "policy": "policy",
}


def orchestrator_agent(state: AgentState):
    """
    Orchestrator agent that classifies user queries into agent categories using LLM.
    """
    messages = state["messages"]

    if not messages:
        return {
            "messages": [AIMessage(content="Routing to: bank agent...")],
            "next": "bank",
        }

    user_query = messages[-1].content

    # Load orchestrator prompt and format with user query
    prompt_template = load_prompt("orchestrator.txt")
    prompt = prompt_template.format(query=user_query)

    # Use LLM to classify the query
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0,
        max_tokens=200,
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Parse JSON response - strip markdown code blocks if present
    content = response.content.strip()
    if content.startswith("```"):
        # Remove markdown code block markers
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:].strip()
    
    try:
        response_json = json.loads(content)
        classification = UserQueryModel(**response_json)
    except (json.JSONDecodeError, Exception) as e:
        # Fallback to bank if parsing fails
        classification = UserQueryModel(category="check_balance", amount=0, followup="")

    # Get the agent name from mapping, default to bank
    agent_key = category_mapping.get(classification.category, "bank")
    next_agent = actions.get(agent_key, actions["default"])

    return {
        "messages": [AIMessage(content=response.content)],
        "next": agent_key,
    }
