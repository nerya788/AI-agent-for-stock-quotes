import requests


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    # --- Auth ---
    def login(self, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
            )
            return (
                response.json()
                if response.status_code == 200
                else {"status": "error", "detail": response.text}
            )
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    def register(self, email, password, full_name):
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "password": password, "full_name": full_name},
            )
            return (
                response.json()
                if response.status_code == 200
                else {"status": "error", "detail": response.text}
            )
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    # --- Watchlist (new fix) ---
    def get_watchlist(self, user_id):
        """Fetch the user's watchlist/portfolio."""
        try:
            response = requests.get(f"{self.base_url}/stocks/watchlist/{user_id}")
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "data": []}
        except Exception as e:
            print(f"API Error (Watchlist): {e}")
            return {"status": "error", "data": []}

    # --- Stocks Data ---
    def get_stock_history(self, symbol):
        try:
            response = requests.get(f"{self.base_url}/stocks/history/{symbol}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"API Error (History): {e}")
            return None

    def get_live_quote(self, symbol):
        try:
            response = requests.get(f"{self.base_url}/stocks/quote/{symbol}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"API Error (Quote): {e}")
            return None

    def get_popular_stocks(self):
        try:
            response = requests.get(f"{self.base_url}/stocks/popular")
            return response.json() if response.status_code == 200 else {"stocks": []}
        except Exception as e:
            print(f"API Error (Popular): {e}")
            return {"stocks": []}

    def get_stock_news(self, symbol, lang: str | None = None):
        """Importance-ranked news for a specific stock.

        lang: 'en' (default) or 'he' to translate to Hebrew on the server side.
        """
        try:
            url = f"{self.base_url}/stocks/news/{symbol}"
            params = {"lang": lang} if lang else None
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return {"symbol": symbol.upper(), "news": []}
        except Exception as e:
            print(f"API Error (News): {e}")
            return {"symbol": symbol.upper(), "news": []}

    # --- AI Features ---
    def get_ai_analysis(self, symbol):
        try:
            response = requests.get(f"{self.base_url}/stocks/analyze/{symbol}")
            return (
                response.json()
                if response.status_code == 200
                else {"analysis": "Error"}
            )
        except Exception as e:
            return {"analysis": f"Connection error: {e}"}

    # --- Trade & Payments ---
    def get_saved_cards(self, user_id):
        """Fetch saved cards (updated endpoint)."""
        try:
            # Updated to /trade/cards/
            response = requests.get(f"{self.base_url}/trade/cards/{user_id}")
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "data": None}
        except Exception as e:
            print(f"API Error (Cards): {e}")
            return {"status": "error", "data": None}

    def post_trade(self, mode, data):
        """Generic function to execute a buy/sell trade."""
        try:
            # mode = 'buy' or 'sell'
            response = requests.post(
                f"{self.base_url}/trade/{mode}", json=data, timeout=10
            )
            return response
        except Exception as e:
            print(f"API Error (Trade): {e}")
            raise e
