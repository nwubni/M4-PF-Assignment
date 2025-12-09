"""
Aggregator agent that combines responses from multiple agents for multi-part queries.
"""

import json
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from src.agents.agent_state import AgentState
from src.utils.prompt_loader import load_prompt
import os
from dotenv import load_dotenv

load_dotenv()


def aggregator_agent(state: AgentState):
    """
    Aggregates responses from multiple agents into a single coherent response.
    """
    messages = state["messages"]
    result = state.get("result", {})
    original_query = result.get("original_query", "")

    # Collect all agent responses (skip orchestrator JSON messages)
    agent_responses = []
    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg, AIMessage):
            content = msg.content
            # Skip orchestrator messages (they contain JSON with category or is_multi_query)
            # Also skip routing messages
            is_orchestrator_msg = (
                "{" in content
                and ("category" in content or "is_multi_query" in content)
            ) or (content in ["Routing to: bank agent..."])

            # Include all other AIMessages (these are agent responses)
            if not is_orchestrator_msg:
                agent_responses.append(content)

    # If we have multiple responses, combine them
    if len(agent_responses) > 1:
        combined_responses = "\n\n".join(
            [f"Part {i+1}: {response}" for i, response in enumerate(agent_responses)]
        )

        # Use LLM to create a coherent combined response
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            max_tokens=1000,
        )

        # Load and format the aggregator prompt
        prompt_template = load_prompt("aggregator.txt")
        prompt = prompt_template.format(
            original_query=original_query, combined_responses=combined_responses
        )

        final_response = llm.invoke([HumanMessage(content=prompt)])
        response_text = final_response.content
    elif len(agent_responses) == 1:
        # Single response, return as is
        response_text = agent_responses[0]
    else:
        # No responses found
        response_text = "I apologize, but I couldn't process your request."

    return {
        "messages": [AIMessage(content=response_text)],
        "next": "END",
    }
