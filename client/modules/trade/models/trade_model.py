from client.core.api_client import APIClient


class TradeModel:
    def __init__(self):
        self.api = APIClient()
        self.current_symbol = ""
        self.current_price = 0.0

    def validate_purchase_input(self, data):
        """Validate purchase input data."""
        errors = []
        if len(data.get("card_number", "")) != 16:
            errors.append("Card number must be 16 digits.")
        if not data.get("card_holder"):
            errors.append("Card holder name is required.")
        if data.get("amount", 0) <= 0:
            errors.append("Quantity must be greater than 0.")
        return errors

    def get_stock_sector(self, symbol):
        """Fetch the sector via the API client."""
        # Use the existing APIClient method that returns quote/info
        info = self.api.get_live_quote(
            symbol
        )  # Or use a dedicated method if it exists in api_client
        if info:
            return info.get("sector", "Technology")
        return "Technology"

    def send_trade_request(self, mode, data):
        """Send a buy/sell request via the main API pipeline."""
        # mode = 'buy' or 'sell'
        return self.api.post_trade(mode, data)

    def get_saved_cards(self, user_id):
        """Fetch and normalize saved cards."""
        response = self.api.get_saved_cards(user_id)

        if response.get("status") == "success":
            raw_data = response.get("data")
            # Wrap into a list as standardized earlier
            final_list = [raw_data] if raw_data else []
            return {"status": "success", "cards": final_list}

        return {"status": "error", "cards": []}
