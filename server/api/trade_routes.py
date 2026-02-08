from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.repositories.stock_repository import StockRepository
from server.dal.supabase_client import SupabaseDAL

# --- נתיב ראשי: /trade ---
router = APIRouter(prefix="/trade", tags=["Trading"])

stock_repo = StockRepository()
dal = SupabaseDAL.get_instance()


# מודלים
class PurchaseRequest(BaseModel):
    symbol: str
    price: float
    amount: int
    card_number: str
    card_holder: str
    expiration: str
    cvv: str
    save_card: bool
    user_id: str = None
    sector: str = "Unknown"


class SaleRequest(BaseModel):
    symbol: str
    current_price: float
    buy_price: float
    amount: int
    event_id: int
    card_number: str
    card_holder: str
    expiration: str
    cvv: str
    user_id: str = None


@router.post("/buy")
async def buy_stock(req: PurchaseRequest):
    print(f"💰 Processing buy request for {req.symbol}...")
    try:
        # שמירת כרטיס אם צריך
        if req.save_card:
            dal.table("saved_cards").insert(
                {
                    "user_id": req.user_id,
                    "card_holder": req.card_holder,
                    "card_number": req.card_number,
                    "expiration": req.expiration,
                    "cvv": req.cvv,
                }
            ).execute()

        # ביצוע הקנייה דרך ה-Repository
        stock_repo.buy_stock(
            symbol=req.symbol,
            price=req.price,
            amount_to_buy=req.amount,
            card_details={"card_number": req.card_number},
            sector=req.sector,
            user_id=req.user_id,
        )
        return {
            "status": "success",
            "message": f"Purchased {req.amount} of {req.symbol}",
        }
    except Exception as e:
        print(f"❌ Purchase failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell")
async def sell_stock(req: SaleRequest):
    print(f"📉 SMART Sale: Selling {req.amount} of {req.symbol} for user {req.user_id}")

    try:
        # 1. עדכון טבלת ה-Watchlist (הטבלה שהדשבורד מציג)
        watchlist_res = (
            dal.table("stocks_watchlist")
            .select("*")
            .eq("symbol", req.symbol)
            .eq("user_id", req.user_id)
            .execute()
        )

        if not watchlist_res.data:
            raise ValueError(f"You don't own {req.symbol} in your watchlist.")

        current_data = watchlist_res.data[0]
        current_qty = current_data.get("amount", 0)

        if req.amount > current_qty:
            raise ValueError(f"Cannot sell {req.amount}, you only own {current_qty}")

        new_qty = current_qty - req.amount

        if new_qty <= 0:
            # אם מכרנו הכל - מוחקים מהדשבורד
            print(f"🗑️ Sold all shares of {req.symbol}. Removing from watchlist.")
            dal.table("stocks_watchlist").delete().eq("symbol", req.symbol).eq(
                "user_id", req.user_id
            ).execute()
        else:
            # אם נשאר חלק - מעדכנים כמות
            print(f"✏️ Updating {req.symbol} quantity to {new_qty}")
            dal.table("stocks_watchlist").update({"amount": new_qty}).eq(
                "symbol", req.symbol
            ).eq("user_id", req.user_id).execute()

        # 2. תיעוד אירוע המכירה בטבלת האירועים (בשביל ההיסטוריה)
        dal.table("stock_events").insert(
            {
                "user_id": req.user_id,
                "symbol": req.symbol,
                "event_type": "STOCK_SOLD",
                "payload": {
                    "amount": req.amount,
                    "price": req.current_price,
                    "total": req.amount * req.current_price,
                },
            }
        ).execute()

        return {
            "status": "success",
            "message": f"Sold {req.amount} shares of {req.symbol}",
        }

    except Exception as e:
        print(f"❌ Sale failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/{user_id}")
async def get_saved_card(user_id: str):
    """
    שליפת הכרטיס האחרון שנשמר
    כתובת מלאה: http://127.0.0.1:8000/trade/cards/USER_ID
    """
    print(f"💳 API: Fetching cards for {user_id}")
    try:
        response = (
            dal.table("saved_cards")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        if response.data:
            print(f"✅ Found card ending in {response.data[0].get('card_number')[-4:]}")
            # מחזירים כאובייקט בודד בתוך data
            return {"status": "success", "data": response.data[0]}
        else:
            print("📭 No cards found")
            return {"status": "success", "data": None}

    except Exception as e:
        print(f"❌ Error fetching card: {e}")
        return {"status": "error", "data": None}
