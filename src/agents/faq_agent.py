"""
FAQ agent for the bank application.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.agent_state import AgentState
from src.utils.vector_lib import get_local_index
from src.utils.prompt_loader import load_prompt

load_dotenv()


def faq_agent(state: AgentState):
    """
    Agent for FAQ operations.
    """
    messages = state["messages"]
    user_query = messages[0].content

    vector_store = get_local_index("faq")
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Retrieve documents
    retrieved_docs = retriever.invoke(user_query)

    prompt_template = load_prompt("faq.txt")
    prompt = prompt_template.format(user_query=user_query, retrieved_docs=retrieved_docs)

    response = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0.7,
        max_tokens=500,
    ).invoke([HumanMessage(content=prompt)])

    return {
        "messages": [AIMessage(content=response.content)],
        "next": "END",
    }
