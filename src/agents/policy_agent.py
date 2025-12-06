"""
Policy agent for the bank application.
"""
import os

from src.agents.agent_state import AgentState
from src.utils.prompt_loader import load_prompt
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage


def policy_agent(state: AgentState):
    """
    Agent for policy operations.
    """
    messages = state["messages"]
    user_query = messages[0].content

    prompt_template = load_prompt("policy.txt")
    prompt = prompt_template.format(user_query=user_query)

    response = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0.7,
        max_tokens=500,
    ).invoke([HumanMessage(content=prompt)])

    return {
        "messages": [AIMessage(content=response.content)],
        "next": "END",
    }
