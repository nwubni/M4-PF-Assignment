"""
Policy agent for the bank application.
"""

from src.utils.rag_agent_factory import create_rag_agent

# Create policy agent using the factory
policy_agent = create_rag_agent(vector_store_name="policy", prompt_file="policy.txt")
