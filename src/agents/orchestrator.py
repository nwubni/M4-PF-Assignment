"""
Orchestrator class that classifies user queries into agent categories.
"""

import os
import sys
import json

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

from langchain_openai import ChatOpenAI
from src.models.user_query_model import UserQueryModel
from src.models.multi_query_model import MultiQueryModel
from src.agents.agent_state import AgentState
from src.utils.prompt_loader import load_prompt
from src.utils.langfuse_utils import get_langfuse_callbacks

# Add path for evaluator import
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


load_dotenv()

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
    Handles both single and multi-part queries.
    """
    messages = state["messages"]
    result = state.get("result", {})

    # Check if we're continuing a multi-query
    if result.get("is_multi_query") and "current_sub_query_index" in result:
        current_index = result["current_sub_query_index"]
        sub_queries = result.get("sub_queries", [])

        # Collect the latest agent response (last message)
        if messages and isinstance(messages[-1], AIMessage):
            responses = result.get("responses", [])
            response_content = messages[-1].content
            responses.append(response_content)
            result["responses"] = responses

        # Check if there are more sub-queries to process
        if current_index + 1 < len(sub_queries):
            # Route to next agent
            next_sub_query = sub_queries[current_index + 1]
            result["current_sub_query_index"] = current_index + 1

            # Update the user query to the next sub-query
            user_query = next_sub_query["query"]
            next_agent = next_sub_query["agent"]

            # Send only the current sub-query
            return {
                "messages": [HumanMessage(content=user_query)],
                "next": next_agent,
                "result": result,
            }
        else:
            # All sub-queries processed, route to aggregator
            # Send original query and all collected responses
            original_query = result.get("original_query", "")
            aggregator_messages = [HumanMessage(content=original_query)]
            for response in result.get("responses", []):
                aggregator_messages.append(AIMessage(content=response))

            return {
                "messages": aggregator_messages,
                "next": "aggregator",
                "result": result,
            }

    if not messages:
        return {
            "messages": [AIMessage(content="Routing to: bank agent...")],
            "next": "bank",
        }

    # Get the original user query (first HumanMessage)
    user_query = None
    for msg in messages:
        if hasattr(msg, "content") and not isinstance(msg, AIMessage):
            user_query = msg.content
            break

    if not user_query:
        user_query = messages[-1].content if messages else ""

    # First, check if this is a multi-part query
    multi_query_prompt_template = load_prompt("orchestrator_multi.txt")
    multi_query_prompt = multi_query_prompt_template.format(query=user_query)

    # Use LangFuse callbacks for monitoring multi-query detection
    callbacks_multi = get_langfuse_callbacks(
        trace_name="orchestrator_multi_query",
        metadata={"agent_type": "orchestrator", "operation": "multi_query_detection"},
    )
    llm_multi = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0,
        max_tokens=500,
        callbacks=callbacks_multi,
    )

    multi_response = llm_multi.invoke([HumanMessage(content=multi_query_prompt)])

    # Parse multi-query response
    multi_content = multi_response.content.strip()
    if multi_content.startswith("```"):
        multi_content = multi_content.split("```")[1]
        if multi_content.startswith("json"):
            multi_content = multi_content[4:].strip()

    try:
        multi_json = json.loads(multi_content)
        multi_query = MultiQueryModel(**multi_json)
    except (json.JSONDecodeError, Exception) as e:
        multi_query = MultiQueryModel(
            is_multi_query=False, sub_queries=[], original_query=user_query
        )

    # If it's a multi-part query, handle it differently
    if multi_query.is_multi_query and len(multi_query.sub_queries) > 1:
        # Store sub-queries in state for processing
        sub_queries_data = {
            "is_multi_query": True,
            "sub_queries": [
                {"query": sq.query, "category": sq.category, "agent": sq.agent}
                for sq in multi_query.sub_queries
            ],
            "current_sub_query_index": 0,
            "responses": [],
            "original_query": user_query,
        }

        # Route to first agent with the first sub-query
        first_sub_query = multi_query.sub_queries[0]
        first_agent = first_sub_query.agent

        # Start with just the first sub-query (original query is stored in result)
        return {
            "messages": [HumanMessage(content=first_sub_query.query)],
            "next": first_agent,
            "result": sub_queries_data,
        }

    # Single query
    prompt_template = load_prompt("orchestrator.txt")
    prompt = prompt_template.format(query=user_query)

    # Use LangFuse callbacks for single query classification
    callbacks_single = get_langfuse_callbacks(
        trace_name="orchestrator_single_query",
        metadata={
            "agent_type": "orchestrator",
            "operation": "single_query_classification",
        },
    )
    llm_single = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0,
        max_tokens=200,
        callbacks=callbacks_single,
    )
    response = llm_single.invoke([HumanMessage(content=prompt)])

    # Parse JSON response and strip markdown code blocks if present
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

    # Get the agent name from mapping. If empty, default to bank
    next_agent = category_mapping.get(classification.category, "bank")

    # If there's a followup question and amount is 0, end here so main.py can display it
    if classification.followup and classification.amount == 0:
        next_agent = "END"

    return {
        "messages": [AIMessage(content=response.content)],
        "next": next_agent,
    }
