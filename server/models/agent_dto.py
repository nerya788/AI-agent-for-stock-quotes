from pydantic import BaseModel
from typing import Optional, Literal


class AgentResponse(BaseModel):
    # Response type: plain message, form request, or trade confirmation
    response_type: Literal["chat", "form", "trade_confirmation"]
    message: str
    # Additional data (only for trade_confirmation)
    trade_payload: Optional[dict] = None
