import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class StockRepository:
    def __init__(self):
        # אתחול החיבור לענן (Supabase) כפי שמופיע בדרישות 
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def add_to_watchlist(self, symbol: str, price: float):
        """
        Command Model: אחראי על הזרקת נתונים לבסיס הנתונים 
        """
        data = {"symbol": symbol, "price": price}
        # ביצוע הפקודה (Command) לעדכון הנתונים [cite: 44, 45]
        return self.supabase.table("stocks_watchlist").insert(data).execute()