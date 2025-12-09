"""
FAQ agent for the bank application.
"""

from src.utils.rag_agent_factory import create_rag_agent

# Create FAQ agent using the factory
faq_agent = create_rag_agent(vector_store_name="faq", prompt_file="faq.txt")
