from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.repositories.stock_repository import StockRepository
from server.dal.supabase_client import SupabaseDAL

router = APIRouter(prefix="/trade", tags=["Trading"])

stock_repo = StockRepository()
dal = SupabaseDAL.get_instance()  # נשמור אותו רק בשביל ה-Saved Cards בינתיים


# --- מודלים ---
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
    amount: int
    user_id: str = None


# --- נתיבים ---


@router.post("/buy")
async def buy_stock(req: PurchaseRequest):
    print(f"💰 API: Processing buy request for {req.symbol}...")
    try:
        # 1. שמירת כרטיס (אפשר להעביר גם את זה ל-Repo בעתיד, אבל כרגע זה בסדר כאן)
        if req.save_card:
            dal.table("saved_cards").upsert(
                {
                    "user_id": req.user_id,
                    "card_holder": req.card_holder,
                    "card_number": req.card_number,
                    "expiration": req.expiration,
                    "cvv": req.cvv,
                },
                on_conflict="user_id",
            ).execute()

        # 2. ביצוע הקנייה דרך ה-Repository (הכל קורה שם!)
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell")
async def sell_stock(req: SaleRequest):
    print(f"📉 API: Requesting sale for {req.symbol}")
    try:
        # --- הניקוי הגדול: קריאה אחת לפונקציה ב-Repo ---
        result = stock_repo.sell_stock(
            symbol=req.symbol,
            amount_to_sell=req.amount,
            current_price=req.current_price,
            user_id=req.user_id,
        )
        return {
            "status": "success",
            "message": f"Sold {req.amount} shares of {req.symbol}",
        }

    except Exception as e:
        print(f"❌ API: Sale failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/{user_id}")
async def get_saved_card(user_id: str):
    # כאן אפשר להשאיר את ה-dal או להעביר ל-Repo.
    # לצורך הניקוי הנוכחי, נתמקד בזה שהמכירה והקנייה עברו ל-Repo.
    response = (
        dal.table("saved_cards").select("*").eq("user_id", user_id).limit(1).execute()
    )
    return {"status": "success", "data": response.data[0] if response.data else None}
