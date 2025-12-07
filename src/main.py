"""
Main file for the bank application.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from src.agents.agent_state import AgentState
from src.enums.agents_enum import AgentsEnum
from src.agents.orchestrator import orchestrator_agent
from src.agents.bank_agent import bank_agent
from src.agents.investments_agent import investment_agent
from src.agents.policy_agent import policy_agent
from src.agents.faq_agent import faq_agent


def create_multi_agent_system():
    """
    Creates a multi-agent system for the bank application.
    """

    workflow = StateGraph(AgentState)

    workflow.add_node(AgentsEnum.ORCHESTRATOR.value, orchestrator_agent)
    workflow.add_node(AgentsEnum.BANK.value, bank_agent)
    workflow.add_node(AgentsEnum.INVESTMENT.value, investment_agent)
    workflow.add_node(AgentsEnum.POLICY.value, policy_agent)
    workflow.add_node(AgentsEnum.FAQ.value, faq_agent)

    workflow.set_entry_point(AgentsEnum.ORCHESTRATOR.value)

    # Define routing function based on the 'next' field in state
    def route_agent(state: AgentState):
        return state.get("next", "END")

    # Add conditional edges from orchestrator to route to appropriate agent
    workflow.add_conditional_edges(
        AgentsEnum.ORCHESTRATOR.value,
        route_agent,
        {
            AgentsEnum.BANK.value: AgentsEnum.BANK.value,
            AgentsEnum.INVESTMENT.value: AgentsEnum.INVESTMENT.value,
            AgentsEnum.POLICY.value: AgentsEnum.POLICY.value,
            AgentsEnum.FAQ.value: AgentsEnum.FAQ.value,
            "END": "__end__",
        }
    )

    # All agents route back to orchestrator or END
    workflow.add_conditional_edges(
        AgentsEnum.BANK.value,
        route_agent,
        {
            AgentsEnum.ORCHESTRATOR.value: AgentsEnum.ORCHESTRATOR.value,
            "END": "__end__",
        }
    )
    
    workflow.add_conditional_edges(
        AgentsEnum.INVESTMENT.value,
        route_agent,
        {
            AgentsEnum.ORCHESTRATOR.value: AgentsEnum.ORCHESTRATOR.value,
            "END": "__end__",
        }
    )
    
    workflow.add_conditional_edges(
        AgentsEnum.POLICY.value,
        route_agent,
        {
            AgentsEnum.ORCHESTRATOR.value: AgentsEnum.ORCHESTRATOR.value,
            "END": "__end__",
        }
    )
    
    workflow.add_conditional_edges(
        AgentsEnum.FAQ.value,
        route_agent,
        {
            AgentsEnum.ORCHESTRATOR.value: AgentsEnum.ORCHESTRATOR.value,
            "END": "__end__",
        }
    )

    return workflow.compile()


def main():
    """
    Main function to run the multi-agent system.
    """
    # Create the multi-agent system
    workflow = create_multi_agent_system()

    print("="*80)
    print("Welcome to the bank application")
    print("="*80)
    print("Type 'exit', 'quit', or 'q' to exit.")
    print("="*80)

    # Track conversation state
    pending_transaction = None  # Store {"category": "deposit", "followup": "..."}
    conversation_messages = []  # Maintain conversation history

    while True:    
        user_input = input("Enter your query: ")

        if user_input.lower() in ["exit", "quit", "q"]:
            break

        # If there's a pending transaction, enhance the query to include context
        if pending_transaction:
            import re
            # Extract numbers from the input (handles "50", "50 dollars", "$50", etc.)
            numbers = re.findall(r'\d+\.?\d*', user_input)
            if numbers:
                amount = float(numbers[0])
                # Construct a query that includes the transaction type and amount
                # This helps the orchestrator understand the context
                user_input = f"I want to {pending_transaction['category']} {amount} dollars"
                pending_transaction = None  # Clear pending transaction
            else:
                # Even if no number, include context so orchestrator can extract amount from natural language
                user_input = f"{pending_transaction['category']}: {user_input}"

        # Add user message to conversation
        conversation_messages.append(HumanMessage(content=user_input))

        result = workflow.invoke(
            AgentState(messages=conversation_messages)
        )

        # Update conversation messages with the result
        if result.get("messages"):
            conversation_messages = result["messages"]
            final_message = result["messages"][-1]
            
            if hasattr(final_message, "content"):
                response_content = final_message.content
                
                # Check if this is an orchestrator response with a followup
                if "{" in response_content and "followup" in response_content:
                    import json
                    try:
                        # Extract JSON from the response
                        json_start = response_content.find("{")
                        json_end = response_content.rfind("}") + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = response_content[json_start:json_end]
                            # Replace single quotes with double quotes
                            json_str = json_str.replace("'", '"')
                            classification = json.loads(json_str)
                            
                            # If there's a followup question, display it and store pending transaction
                            if classification.get("followup"):
                                print(classification["followup"])
                                pending_transaction = {
                                    "category": classification.get("category", ""),
                                    "followup": classification.get("followup", "")
                                }
                            else:
                                print(response_content)
                        else:
                            print(response_content)
                    except (json.JSONDecodeError, Exception):
                        print(response_content)
                else:
                    print(response_content)
            else:
                print(result)
        else:
            print(result)


if __name__ == "__main__":
    main()
