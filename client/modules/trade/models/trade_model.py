from client.core.api_client import APIClient
import requests

class TradeModel:
    def __init__(self):
        self.api = APIClient() # הנחה שזה קיים אצלך
        self.current_symbol = ""
        self.current_price = 0.0
        # כתובת בסיס לגיבוי
        self.base_url = "http://127.0.0.1:8000"

    def validate_purchase_input(self, data):
        """בדיקות תקינות לנתוני קנייה"""
        errors = []
        if len(data.get('card_number', '')) != 16:
            errors.append("Card number must be 16 digits.")
        if not data.get('card_holder'):
            errors.append("Card holder name is required.")
        if data.get('amount', 0) <= 0:
            errors.append("Quantity must be greater than 0.")
        return errors

    def get_stock_sector(self, symbol):
        """שליפת הסקטור האמיתי מהשרת"""
        try:
            response = requests.get(f"{self.base_url}/stocks/info/{symbol}", timeout=3)
            if response.status_code == 200:
                return response.json().get('sector', 'Unknown')
        except:
            pass
        return "Technology" 

    def send_trade_request(self, endpoint, data):
        """שליחת בקשת קנייה/מכירה לשרת"""
        url = f"{self.base_url}/trade/{endpoint}"
        return requests.post(url, json=data, timeout=5)

    def get_saved_cards(self, user_id):
        """
        התיקון הקריטי!
        שליפה מהשרת ועטיפה ברשימה [] עבור ה-View
        """
        try:
            # עוקפים את APIClient כדי להיות בטוחים בנתיב
            url = f"{self.base_url}/trade/cards/{user_id}"
            print(f"📡 Model: Connecting directly to {url}...")
            
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                json_data = response.json() # השרת מחזיר {status:..., data: {...}}
                raw_data = json_data.get("data")
                
                print(f"📡 Model: Raw data received: {raw_data}")

                # --- כאן הקסם קורה ---
                final_list = []
                
                if raw_data is None:
                    final_list = []
                elif isinstance(raw_data, list):
                    final_list = raw_data
                elif isinstance(raw_data, dict):
                    # אם זה מילון (אובייקט בודד), נכניס אותו לרשימה!
                    final_list = [raw_data]
                
                print(f"✅ Model: Passing list of {len(final_list)} cards to Controller")
                return {"status": "success", "cards": final_list}
            
            return {"status": "error", "cards": []}

        except Exception as e:
            print(f"❌ Model Error: {e}")
            return {"status": "error", "cards": []}