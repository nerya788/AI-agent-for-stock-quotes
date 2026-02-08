from server.dal.supabase_client import SupabaseDAL

class StockRepository:
    def __init__(self):
        # אך ורק self.dal!
        self.dal = SupabaseDAL.get_instance()

    def _append_event(self, symbol: str, event_type: str, payload: dict, user_id: str = None):
        """
        תיעוד אירוע בטבלת ההיסטוריה.
        """
        event_data = {
            "symbol": symbol,
            "event_type": event_type,
            "payload": payload,
            "user_id": user_id 
        }
        try:
            self.dal.table("stock_events").insert(event_data).execute()
            print(f"📝 Event Logged: {event_type} for {symbol} (User: {user_id})")
        except Exception as e:
            print(f"❌ Failed to log event inside _append_event: {e}")

    def get_watchlist(self):
        return self.dal.table("stocks_watchlist").select("*").execute()

    def add_to_watchlist(self, symbol: str, price: float, user_id: str = None):
        self._append_event(symbol, "STOCK_ADDED", {
            "price": price, 
            "amount": 0,
            "total": 0,
            "source": "manual_add"
        }, user_id)

        view_data = {"symbol": symbol, "price": price, "amount": 0, "user_id": user_id}
        return self.dal.table("stocks_watchlist").upsert(view_data).execute()

    def remove_from_watchlist(self, symbol: str, user_id: str = None):
        self._append_event(symbol, "STOCK_REMOVED", {
            "amount": 0, "price": 0, "total": 0
        }, user_id)
        return self.dal.table("stocks_watchlist").delete().eq("symbol", symbol).eq("user_id", user_id).execute()

    def get_events_history(self, symbol: str):
        return self.dal.table("stock_events")\
            .select("*")\
            .eq("symbol", symbol)\
            .order("created_at", desc=True)\
            .execute()

    def buy_stock(self, symbol: str, price: float, amount_to_buy: int, card_details: dict = None, sector: str = "Unknown", user_id: str = None):
        """
        ביצוע קנייה חכמה: חישוב ממוצע משוקלל + תיעוד
        """
        print(f"🔄 Starting SMART buy_stock for {symbol}...")

        # 1. תיעוד האירוע
        self._append_event(symbol, "STOCK_PURCHASED", {
            "amount": amount_to_buy,
            "price": price,
            "total": price * amount_to_buy,
            "payment_info": card_details.get("card_number")[-4:] if card_details else "N/A"
        }, user_id=user_id)

        # 2. חישוב הממוצע המשוקלל
        try:
            existing_row = self.dal.table("stocks_watchlist")\
                .select("*")\
                .eq("symbol", symbol)\
                .eq("user_id", user_id)\
                .execute()
            
            new_total_amount = amount_to_buy
            new_avg_price = price
            
            if existing_row.data and len(existing_row.data) > 0:
                current_data = existing_row.data[0]
                current_amount = current_data.get('amount', 0)
                current_avg_price = current_data.get('price', 0)

                # חישוב משוקלל
                if current_amount + amount_to_buy > 0:
                    total_cost = (current_amount * current_avg_price) + (amount_to_buy * price)
                    new_total_amount = current_amount + amount_to_buy
                    new_avg_price = total_cost / new_total_amount
            
            # 3. שמירה
            view_data = {
                "user_id": user_id,
                "symbol": symbol,
                "price": new_avg_price, 
                "amount": new_total_amount,
                "sector": sector
            }
            
            print(f"💾 Saving SMART data: {view_data}")
            return self.dal.table("stocks_watchlist").upsert(view_data, on_conflict="user_id, symbol").execute()

        except Exception as e:
            print(f"❌ Error in buy_stock: {e}")
            raise e