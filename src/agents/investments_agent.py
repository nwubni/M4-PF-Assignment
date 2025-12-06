import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.agent_state import AgentState
from src.enums.agents_enum import AgentsEnum
from src.utils.vector_lib import get_local_index

load_dotenv()


def investment_agent(state: AgentState):
    """
    Agent for investments operations.
    """
    messages = state["messages"]
    user_query = messages[0].content

    vector_store = get_local_index(AgentsEnum.INVESTMENT)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Retrieve documents
    retrieved_docs = retriever.invoke(user_query)

    prompt = f"""
    You are a investments operations agent.
    You are given a user query and you need to respond to it. You are an expert in investments and you are able to answer questions about investments.
    The user query is: {user_query}
    The retrieved documents are: {retrieved_docs}
    """

    response = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=6,
        max_tokens=130,
    ).invoke([HumanMessage(content=prompt)])

    return {
        "messages": [AIMessage(content=response.content)],
        "next": AgentsEnum.INVESTMENT,
    }