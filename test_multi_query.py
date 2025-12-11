"""
Test script for multi-query functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage
from src.agents.agent_state import AgentState
from src.main import create_multi_agent_system


def test_multi_query():
    """Test multi-query handling"""
    workflow = create_multi_agent_system()

    # Test query
    query = "What investment options do you have, and what is my account balance?"

    print(f"\n{'='*80}")
    print(f"Testing multi-query: {query}")
    print(f"{'='*80}\n")

    result = workflow.invoke(AgentState(messages=[HumanMessage(content=query)]))

    print(f"\n{'='*80}")
    print("RESULT:")
    print(f"{'='*80}")
    print(f"Messages: {len(result['messages'])}")
    for i, msg in enumerate(result["messages"]):
        print(f"\nMessage {i+1} ({type(msg).__name__}):")
        print(
            f"  {msg.content[:200]}..."
            if len(msg.content) > 200
            else f"  {msg.content}"
        )

    print(f"\nNext: {result.get('next', 'N/A')}")
    print(f"Result metadata: {result.get('result', {})}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_multi_query()
