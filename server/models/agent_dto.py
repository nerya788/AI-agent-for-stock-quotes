from pydantic import BaseModel
from typing import Optional, Literal

class AgentResponse(BaseModel):
    # סוג התשובה: סתם הודעה, בקשת טופס, או אישור עסקה
    response_type: Literal["chat", "form", "trade_confirmation"] 
    message: str
    # נתונים נוספים (רק אם זה trade_confirmation)
    trade_payload: Optional[dict] = None