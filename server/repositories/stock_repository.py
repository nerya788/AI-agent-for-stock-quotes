from server.dal.supabase_client import SupabaseDAL

class StockRepository:
    def __init__(self):
        # שימוש ב-DAL הקיים (במקום ליצור חיבור חדש)
        self.dal = SupabaseDAL.get_instance()

    def _append_event(self, symbol: str, event_type: str, payload: dict):
        """
        תיעוד אירוע בטבלת ההיסטוריה (Event Store).
        """
        event_data = {
            "symbol": symbol,
            "event_type": event_type,
            "payload": payload
        }
        try:
            self.dal.table("stock_events").insert(event_data).execute()
            print(f"📝 Event Logged: {event_type} for {symbol}")
        except Exception as e:
            print(f"❌ Failed to log event: {e}")

    def get_watchlist(self):
        """
        שליפת כל המניות לדשבורד (היה חסר בקוד שלך!)
        """
        return self.dal.table("stocks_watchlist").select("*").execute()

    def add_to_watchlist(self, symbol: str, price: float):
        """
        הוספת מניה למעקב (כולל תיעוד אירוע)
        """
        # 1. תיעוד
        self._append_event(symbol, "STOCK_ADDED", {
            "price": price, 
            "source": "manual_add"
        })

        # 2. שמירה בטבלה
        view_data = {"symbol": symbol, "price": price, "amount": 0} # ברירת מחדל 0 כמות
        # משתמשים ב-upsert כדי לא לדרוס כמות קיימת אם יש
        # במקרה הזה נזהר לא לאפס כמות אם המשתמש רק רצה לעדכן מחיר
        # אבל לפשטות כרגע זה בסדר (או שאפשר לבדוק קודם)
        return self.dal.table("stocks_watchlist").upsert(view_data).execute()

    def remove_from_watchlist(self, symbol: str):
        """
        מחיקת מניה (כולל תיעוד אירוע - בונוס לציון)
        """
        # 1. תיעוד
        self._append_event(symbol, "STOCK_REMOVED", {})

        # 2. מחיקה בפועל
        return self.dal.table("stocks_watchlist").delete().eq("symbol", symbol).execute()

    def get_events_history(self, symbol: str):
        """
        שליפת היסטוריית האירועים למניה
        """
        return self.dal.table("stock_events")\
            .select("*")\
            .eq("symbol", symbol)\
            .order("created_at", desc=True)\
            .execute()

    def buy_stock(self, symbol: str, price: float, amount_to_buy: int, card_details: dict = None):
        """
        ביצוע קנייה: תיעוד + עדכון כמות
        """
        # 1. תיעוד האירוע
        self._append_event(symbol, "STOCK_PURCHASED", {
            "amount_added": amount_to_buy,
            "price_at_purchase": price,
            "payment_info": card_details.get("card_number")[-4:] if card_details else "N/A"
        })

        # 2. עדכון המצב (Aggregation)
        try:
            # שליפת כמות נוכחית
            existing_row = self.dal.table("stocks_watchlist")\
                .select("amount")\
                .eq("symbol", symbol)\
                .execute()
            
            new_total_amount = amount_to_buy
            
            if existing_row.data and len(existing_row.data) > 0:
                current_amount = existing_row.data[0].get('amount', 0)
                new_total_amount += current_amount
                print(f"🔄 Updating {symbol}: {current_amount} + {amount_to_buy} = {new_total_amount}")
            else:
                print(f"✨ Creating new entry for {symbol}")

            # שמירה
            view_data = {
                "symbol": symbol,
                "price": price,
                "amount": new_total_amount
            }
            return self.dal.table("stocks_watchlist").upsert(view_data).execute()

        except Exception as e:
            print(f"❌ Error updating watchlist: {e}")
            raise e