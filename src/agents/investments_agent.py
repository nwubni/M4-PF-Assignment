"""
Investment agent for the bank application.
"""

from src.utils.rag_agent_factory import create_rag_agent

# Create investment agent using the factory
investment_agent = create_rag_agent(
    vector_store_name="investment", prompt_file="investment.txt"
)
