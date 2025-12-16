"""
Aggregator agent that combines responses from multiple agents for multi-part queries.
"""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.agent_state import AgentState

load_dotenv()


def aggregator_agent(state: AgentState):
    """
    Aggregates responses from multiple agents into a single coherent response.
    """
    result = state.get("result", {})
    original_query = result.get("original_query", "")

    # Get responses directly from the result state (collected by orchestrator)
    # This avoids duplicates from message history
    agent_responses = result.get("responses", [])

    # If we have multiple responses, combine them directly
    if len(agent_responses) > 1:
        # Simply join the responses with newlines - no LLM needed
        response_text = "\n".join(agent_responses)
    elif len(agent_responses) == 1:
        # Single response, return as is
        response_text = agent_responses[0]
    else:
        # No responses found
        response_text = "I apologize, but I couldn't process your request."

    # Return only the aggregated response and clear previous messages
    # Get the original query from state
    result = state.get("result", {})
    original_query = result.get("original_query", "")

    return {
        "messages": [
            HumanMessage(content=original_query),
            AIMessage(content=response_text),
        ],
        "next": "END",
    }
