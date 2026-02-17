class AdvisorModel:
    def __init__(self, response_type: str, message: str, trade_payload: dict = None):
        self.response_type = response_type # "chat", "form", "trade_confirmation"
        self.message = message
        self.trade_payload = trade_payload

    @classmethod
    def from_json(cls, data: dict):
        """ממיר את תשובת השרת לאובייקט פייתון נוח"""
        return cls(
            response_type=data.get("response_type", "chat"),
            message=data.get("message", ""),
            trade_payload=data.get("trade_payload")
        )

    # אפשר להוסיף כאן לוגיקה נוחה
    def is_trade(self):
        return self.response_type == "trade_confirmation"

    def is_form(self):
        return self.response_type == "form"