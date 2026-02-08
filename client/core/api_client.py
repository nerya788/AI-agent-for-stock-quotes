import requests

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    # --- Auth ---
    def login(self, email, password):
        try:
            response = requests.post(f"{self.base_url}/auth/login", json={
                "email": email,
                "password": password
            })
            return response.json() if response.status_code == 200 else {"status": "error", "detail": response.text}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    def register(self, email, password, full_name):
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                "email": email,
                "password": password,
                "full_name": full_name
            })
            return response.json() if response.status_code == 200 else {"status": "error", "detail": response.text}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    # --- Watchlist (התיקון החדש) ---
    def get_watchlist(self, user_id):
        """שליפת רשימת המעקב/פורטפוליו של המשתמש"""
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

    # --- AI Features ---
    def get_ai_analysis(self, symbol):
        try:
            response = requests.get(f"{self.base_url}/stocks/analyze/{symbol}")
            return response.json() if response.status_code == 200 else {"analysis": "Error"}
        except Exception as e:
            return {"analysis": f"Connection error: {e}"}

    # --- Trade & Payments ---
    def get_saved_cards(self, user_id):
        """קבלת כרטיסים שמורים (הנתיב המעודכן)"""
        try:
            # שינינו ל-/trade/cards/
            response = requests.get(f"{self.base_url}/trade/cards/{user_id}")
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "data": None}
        except Exception as e:
            print(f"API Error (Cards): {e}")
            return {"status": "error", "data": None}

    def post_trade(self, mode, data):
        """פונקציה גנרית לביצוע קנייה/מכירה"""
        try:
            # mode = 'buy' או 'sell'
            response = requests.post(f"{self.base_url}/trade/{mode}", json=data, timeout=10)
            return response
        except Exception as e:
            print(f"API Error (Trade): {e}")
            raise e