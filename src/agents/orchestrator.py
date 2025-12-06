"""
Orchestrator class that classifies user queries into agent categories.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

# Add path for evaluator import
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.agents.agent_state import AgentState

load_dotenv()


model_name = os.getenv("LLM_MODEL", "gpt-4")

actions = {
    "bank": "bank_agent",
    "policy": "policy_agent",
    "faq": "faq_agent",
    "default": "default_agent",
}


def orchestrator_agent(state: AgentState):
    """
    Orchestrator agent that classifies user queries into agent categories.
    """

    messages = state["messages"]
    last_message = messages[-1].content | "default_agent"
    next_agent = actions.get(last_message, "default_agent")

    return {
        "messages": [AIMessage(content=f"Routing to: {next_agent} agent...")],
        "next": next_agent,
    }
