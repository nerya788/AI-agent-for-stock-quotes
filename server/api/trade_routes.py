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
    user_id: str = None  # ה-UUID של המשתמש מ-Supabase Auth

class SaleRequest(BaseModel):
    symbol: str
    current_price: float
    buy_price: float
    amount: int
    card_number: str
    card_holder: str
    expiration: str
    cvv: str
    user_id: str = None  # ה-UUID של המשתמש מ-Supabase Auth

@router.post("/buy")
async def buy_stock(req: PurchaseRequest):
    """
    נקודת הקצה (Endpoint) שמקבלת את הבקשה מהלקוח
    """
    print(f"💰 Processing purchase request for {req.symbol}...")
    
    try:
        # 1. שמירת כרטיס (אם המשתמש ביקש) - כולל user_id
        if req.save_card:
            dal.table("saved_cards").insert({
                "user_id": req.user_id,  # הוסף את user_id
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


@router.get("/saved-cards/{user_id}")
async def get_saved_cards(user_id: str):
    """
    קבלת כל הכרטיסים השמורים של משתמש מסוים
    """
    try:
        response = dal.table("saved_cards").select("*").eq("user_id", user_id).execute()
        cards = response.data if response.data else []
        print(f"📋 Retrieved {len(cards)} saved cards for user {user_id}")
        return {"status": "success", "cards": cards}
    except Exception as e:
        print(f"❌ Failed to retrieve saved cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell")
async def sell_stock(req: SaleRequest):
    """
    נקודת הקצה (Endpoint) לביצוע מכירת מניה
    """
    print(f"📉 Processing sale request for {req.symbol}...")
    
    try:
        # קבל את כל ה-purchase events של המשתמש עבור המניה הזו
        response = dal.table("stock_events").select("*").eq("user_id", req.user_id).eq("symbol", req.symbol).eq("event_type", "STOCK_PURCHASED").execute()
        purchase_events = response.data if response.data else []
        
        print(f"📋 Found {len(purchase_events)} purchase events for {req.symbol}")
        
        if not purchase_events:
            raise ValueError(f"No purchase records found for {req.symbol}")
        
        # מחק events לפי הכמות שמוכרים
        remaining_to_delete = req.amount
        deleted_count = 0
        
        for event in purchase_events:
            if remaining_to_delete <= 0:
                break
            
            event_id = event.get("id")
            event_amount = event.get("payload", {}).get("amount", 0)
            
            print(f"  🗑️ Deleting event {event_id}: {event_amount} shares")
            
            # מחק את ה-event
            dal.table("stock_events").delete().eq("id", event_id).execute()
            deleted_count += 1
            remaining_to_delete -= event_amount
        
        print(f"✅ Deleted {deleted_count} purchase events for {req.symbol}")
        print(f"✅ Sale completed: {req.amount} shares of {req.symbol}")
        
        return {"status": "success", "message": f"Sold {req.amount} of {req.symbol}"}
        
    except Exception as e:
        print(f"❌ Sale failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))