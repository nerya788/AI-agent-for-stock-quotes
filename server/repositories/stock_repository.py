from server.dal.supabase_client import SupabaseDAL


class StockRepository:
    def __init__(self):
        # Use only self.dal!
        self.dal = SupabaseDAL.get_instance()

    def record_event(self, symbol: str, event_type: str, payload: dict, user_id: str):
        """
        Save an event into the history table (logic centralized in the Repo).
        """
        event_data = {
            "user_id": user_id,
            "symbol": symbol.upper(),
            "event_type": event_type,
            "payload": payload,
            # `created_at` is set automatically in the DB (or could be set here)
        }
        return self.dal.table("stock_events").insert(event_data).execute()

    def get_watchlist(self, user_id: str = None):
        query = self.dal.table("stocks_watchlist").select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        return query.execute()

    def add_to_watchlist(self, symbol: str, price: float, user_id: str = None):
        self.record_event(
            symbol,
            "STOCK_ADDED",
            {"price": price, "amount": 0, "total": 0, "source": "manual_add"},
            user_id,
        )

        view_data = {"symbol": symbol, "price": price, "amount": 0, "user_id": user_id}
        return self.dal.table("stocks_watchlist").upsert(view_data).execute()

    def remove_from_watchlist(self, symbol: str, user_id: str = None):
        self.record_event(
            symbol, "STOCK_REMOVED", {"amount": 0, "price": 0, "total": 0}, user_id
        )
        return (
            self.dal.table("stocks_watchlist")
            .delete()
            .eq("symbol", symbol)
            .eq("user_id", user_id)
            .execute()
        )

    def get_events_history(self, symbol: str):
        return (
            self.dal.table("stock_events")
            .select("*")
            .eq("symbol", symbol)
            .order("created_at", desc=True)
            .execute()
        )

    def buy_stock(
        self,
        symbol: str,
        price: float,
        amount_to_buy: int,
        card_details: dict = None,
        sector: str = "Unknown",
        user_id: str = None,
    ):
        """
        Smart buy execution: weighted average calculation + event logging.
        """
        print(f"🔄 Starting SMART buy_stock for {symbol}...")

        # 1. Log the event
        self.record_event(
            symbol,
            "STOCK_PURCHASED",
            {
                "amount": amount_to_buy,
                "price": price,
                "total": price * amount_to_buy,
                "payment_info": (
                    card_details.get("card_number")[-4:] if card_details else "N/A"
                ),
            },
            user_id=user_id,
        )

        # 2. Compute the weighted average
        try:
            existing_row = (
                self.dal.table("stocks_watchlist")
                .select("*")
                .eq("symbol", symbol)
                .eq("user_id", user_id)
                .execute()
            )

            new_total_amount = amount_to_buy
            new_avg_price = price

            if existing_row.data and len(existing_row.data) > 0:
                current_data = existing_row.data[0]
                current_amount = current_data.get("amount", 0)
                current_avg_price = current_data.get("price", 0)

                # Weighted calculation
                if current_amount + amount_to_buy > 0:
                    total_cost = (current_amount * current_avg_price) + (
                        amount_to_buy * price
                    )
                    new_total_amount = current_amount + amount_to_buy
                    new_avg_price = total_cost / new_total_amount

            # 3. Persist
            view_data = {
                "user_id": user_id,
                "symbol": symbol,
                "price": new_avg_price,
                "amount": new_total_amount,
                "sector": sector,
            }

            print(f"💾 Saving SMART data: {view_data}")
            return (
                self.dal.table("stocks_watchlist")
                .upsert(view_data, on_conflict="user_id, symbol")
                .execute()
            )

        except Exception as e:
            print(f"❌ Error in buy_stock: {e}")
            raise e

    def sell_stock(
        self,
        symbol: str,
        amount_to_sell: int,
        current_price: float,
        user_id: str = None,
    ):
        """
        Centralized sell logic: update quantity or delete if everything was sold.
        """
        print(f"📉 Repository: Processing sale for {symbol}...")

        try:
            # 1. Check current state in the watchlist
            watchlist_res = (
                self.dal.table("stocks_watchlist")
                .select("*")
                .eq("symbol", symbol)
                .eq("user_id", user_id)
                .execute()
            )

            if not watchlist_res.data:
                raise ValueError(f"No shares found for {symbol}")

            current_data = watchlist_res.data[0]
            current_qty = current_data.get("amount", 0)

            if amount_to_sell > current_qty:
                raise ValueError(f"Insufficient shares. Available: {current_qty}")

            new_qty = current_qty - amount_to_sell

            # 2. Apply the action: update or delete
            if new_qty <= 0:
                self.dal.table("stocks_watchlist").delete().eq("symbol", symbol).eq(
                    "user_id", user_id
                ).execute()
            else:
                self.dal.table("stocks_watchlist").update({"amount": new_qty}).eq(
                    "symbol", symbol
                ).eq("user_id", user_id).execute()

            # 3. Log the event in history
            self.record_event(
                symbol,
                "STOCK_SOLD",
                {
                    "amount": amount_to_sell,
                    "price": current_price,
                    "total": amount_to_sell * current_price,
                },
                user_id=user_id,
            )

            return {"status": "success", "remaining_qty": new_qty}

        except Exception as e:
            print(f"❌ Error in sell_stock logic: {e}")
            raise e
