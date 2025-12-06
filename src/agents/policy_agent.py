"""
Policy agent for the bank application.
"""

from agents.agent import Agent


class PolicyAgent(Agent):
    """
    Agent for policy.
    """

    def __init__(self, name):
        """
        Initialize the policy agent.
        """
        super().__init__(name)

    def run(self):
        """
        Run the policy agent.
        """
