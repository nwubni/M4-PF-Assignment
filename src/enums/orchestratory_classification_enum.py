"""
Orchestrator classification enums.
"""

from enum import Enum


class OrchestratorClassificationEnum(Enum):
    """Enum for orchestrator classification types."""

    FAQ = "faq"
    INVESTMENT = "investment"
    POLICY = "policy"
    BANK = "bank"
    AGGREGATOR = "aggregator"
    END = "end"
