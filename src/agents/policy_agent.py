"""
Policy agent for the bank application.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.agent_state import AgentState
from src.enums.agents_enum import AgentsEnum
from src.utils.vector_lib import get_local_index
from src.utils.prompt_loader import load_prompt

load_dotenv()


def policy_agent(state: AgentState):
    """
    Agent for policy operations.
    """
    messages = state["messages"]
    # Get the last HumanMessage (could be a sub-query in multi-query scenarios)
    user_query = None
    for msg in reversed(messages):
        if hasattr(msg, "content") and not isinstance(msg, AIMessage):
            user_query = msg.content
            break

    if not user_query:
        user_query = messages[0].content if messages else ""

    vector_store = get_local_index("policy")
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Retrieve documents
    retrieved_docs = retriever.invoke(user_query)

    prompt_template = load_prompt("policy.txt")
    prompt = prompt_template.format(
        user_query=user_query, retrieved_docs=retrieved_docs
    )

    response = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0.7,
        max_tokens=500,
    ).invoke([HumanMessage(content=prompt)])

    # Check if this is part of a multi-query
    result = state.get("result", {})
    if result.get("is_multi_query"):
        # In multi-query, return only the response and route back to orchestrator
        return {
            "messages": [AIMessage(content=response.content)],
            "next": AgentsEnum.ORCHESTRATOR.value,
            "result": result,
        }

    return {
        "messages": [AIMessage(content=response.content)],
        "next": "END",
    }
