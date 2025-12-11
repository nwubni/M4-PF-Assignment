"""
Simple test for multi-query functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage
from src.agents.agent_state import AgentState
from src.main import create_multi_agent_system


def main():
    workflow = create_multi_agent_system()

    # Test multi-query
    query = "What investment options do you have, and what is my account balance?"
    print(f"\nQuery: {query}\n")
    print("=" * 80)

    result = workflow.invoke(AgentState(messages=[HumanMessage(content=query)]))

    print("\n" + "=" * 80)
    print("FINAL RESPONSE:")
    print("=" * 80)

    # Get the last AI message (should be from aggregator)
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and msg.__class__.__name__ == "AIMessage":
            print(msg.content)
            break

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
