"""
FAQ agent for the bank application.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.agent_state import AgentState
from src.enums.agents_enum import AgentsEnum

load_dotenv()


def faq_agent(state: AgentState):
    """
    Agent for FAQ operations.
    """
    messages = state["messages"]
    user_query = messages[0].content

    prompt = f"""
    You are a FAQ operations agent.
    You are given a user query and you need to respond to it.
    The user query is: {user_query}
    """

    response = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=6,
        max_tokens=130,
    ).invoke([HumanMessage(content=prompt)])

    return {
        "messages": [AIMessage(content=response.content)],
        "next": AgentsEnum.FAQ,
    }
