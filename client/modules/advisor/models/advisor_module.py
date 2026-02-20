class AdvisorModel:
    def __init__(self, response_type: str, message: str, trade_payload: dict = None):
        self.response_type = response_type  # "chat", "form", "trade_confirmation"
        self.message = message
        self.trade_payload = trade_payload

    @classmethod
    def from_json(cls, data: dict):
        """Convert the server response into a convenient Python object."""
        return cls(
            response_type=data.get("response_type", "chat"),
            message=data.get("message", ""),
            trade_payload=data.get("trade_payload"),
        )

    # Convenience logic can be added here
    def is_trade(self):
        return self.response_type == "trade_confirmation"

    def is_form(self):
        return self.response_type == "form"
