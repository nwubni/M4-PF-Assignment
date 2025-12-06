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


def create_multi_agent_system() -> StateGraph:
    """
    Creates a multi-agent system for the bank application.
    """

    workflow = StateGraph(AgentState)

    workflow.add_node(AgentsEnum.ORCHESTRATOR, orchestrator_agent)
    workflow.add_node(AgentsEnum.BANK, bank_agent)
    workflow.add_node(AgentsEnum.INVESTMENT, investment_agent)
    workflow.add_node(AgentsEnum.POLICY, policy_agent)
    workflow.add_node(AgentsEnum.FAQ, faq_agent)

    workflow.set_entry_point(AgentsEnum.ORCHESTRATOR)

    workflow.add_edge(AgentsEnum.ORCHESTRATOR, AgentsEnum.BANK)
    workflow.add_edge(AgentsEnum.BANK, AgentsEnum.ORCHESTRATOR)

    return workflow.compile()


def main():
    result = orchestrator_agent(AgentState(messages=[HumanMessage(content="I want to deposit 500 Naira.")]))
    print(result)


if __name__ == "__main__":
    main()
