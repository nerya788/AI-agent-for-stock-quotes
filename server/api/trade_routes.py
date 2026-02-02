from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.repositories.stock_repository import StockRepository
from server.dal.supabase_client import SupabaseDAL

router = APIRouter(prefix="/trade", tags=["Trading"])

# יצירת המופעים (Instances)
stock_repo = StockRepository()
dal = SupabaseDAL.get_instance()

# המודל של הבקשה (מה הלקוח שולח)
class PurchaseRequest(BaseModel):
    symbol: str
    price: float
    amount: int
    card_number: str
    card_holder: str
    expiration: str
    cvv: str
    save_card: bool

@router.post("/buy")
async def buy_stock(req: PurchaseRequest):
    """
    נקודת הקצה (Endpoint) שמקבלת את הבקשה מהלקוח
    """
    print(f"💰 Processing purchase request for {req.symbol}...")
    
    try:
        # 1. שמירת כרטיס (אם המשתמש ביקש) - פעולה פשוטה אפשר לעשות כאן או ב-Repo
        if req.save_card:
            dal.table("saved_cards").insert({
                "card_holder": req.card_holder,
                "card_number": req.card_number,
                "expiration": req.expiration,
                "cvv": req.cvv
            }).execute()

        # 2. קריאה ללוגיקה העסקית שנמצאת ב-Repository
        # אנחנו מעבירים את הנתונים מתוך האובייקט req
        stock_repo.buy_stock(
            symbol=req.symbol,
            price=req.price,
            amount_to_buy=req.amount,
            card_details={"card_number": req.card_number}
        )
        
        return {"status": "success", "message": f"Purchased {req.amount} of {req.symbol}"}
        
    except Exception as e:
        print(f"❌ Purchase failed: {e}")
        # החזרת שגיאה מסודרת ללקוח כדי שיציג הודעה מתאימה
        raise HTTPException(status_code=500, detail=str(e))