import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class StockRepository:
    def __init__(self):
        # Initialize cloud connection (Supabase) as specified in requirements
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def add_to_watchlist(self, symbol: str, price: float):
        """
        Command Model: Responsible for injecting data into the database
        """
        data = {"symbol": symbol, "price": price}
        # Execute the command to update the data [cite: 44, 45]
        return self.supabase.table("stocks_watchlist").insert(data).execute()