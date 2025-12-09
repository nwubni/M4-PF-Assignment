"""
Utility for loading prompt templates from files.
"""

import os


def load_prompt(filename: str) -> str:
    """
    Load prompt template from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., 'bank.txt')

    Returns:
        The prompt template as a string
    """
    # Get the project root by going up from utils directory
    utils_dir = os.path.dirname(__file__)
    prompts_dir = os.path.join(utils_dir, "..", "prompts")
    prompt_path = os.path.join(prompts_dir, filename)

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
