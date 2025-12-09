from pydantic import BaseModel


class UserQueryModel(BaseModel):
    """Model for user query classification."""

    category: str
    amount: float
    followup: str
