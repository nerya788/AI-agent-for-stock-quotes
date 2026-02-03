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
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "detail": response.text}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    def register(self, email, password, full_name):
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                "email": email,
                "password": password,
                "full_name": full_name
            })
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "detail": response.text}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    # --- Stocks Data (Explorer & Portfolio) ---
    def get_stock_history(self, symbol):
        """פונקציה חדשה לגרפים"""
        try:
            response = requests.get(f"{self.base_url}/stocks/history/{symbol}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"API Error (History): {e}")
            return None

    def get_live_quote(self, symbol):
        """פונקציה למחיר בזמן אמת"""
        try:
            response = requests.get(f"{self.base_url}/stocks/quote/{symbol}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"API Error (Quote): {e}")
            return None

    def get_popular_stocks(self):
        """רשימת חברות פופולריות עבור Browse"""
        try:
            response = requests.get(f"{self.base_url}/stocks/popular")
            if response.status_code == 200:
                return response.json()
            return {"stocks": []}
        except Exception as e:
            print(f"API Error (Popular): {e}")
            return {"stocks": []}

    # --- AI Features ---
    def get_ai_analysis(self, symbol):
        """למודול ה-Advisor"""
        try:
            response = requests.get(f"{self.base_url}/stocks/analyze/{symbol}")
            if response.status_code == 200:
                return response.json()
            return {"analysis": "Error fetching analysis"}
        except Exception as e:
            return {"analysis": f"Connection error: {e}"}

    def get_investment_plan(self, data):
        """לשאלון ההשקעות בפורטפוליו"""
        try:
            # הגדלנו timeout כי זה לוקח זמן
            response = requests.post(f"{self.base_url}/stocks/ai-investment-plan", json=data, timeout=120)
            if response.status_code == 200:
                return response.json()
            return {"recommendation": f"Error: {response.text}"}
        except Exception as e:
            return {"recommendation": f"Connection error: {e}"}