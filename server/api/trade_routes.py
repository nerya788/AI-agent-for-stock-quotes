from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.repositories.stock_repository import StockRepository
from server.dal.supabase_client import SupabaseDAL

router = APIRouter(prefix="/trade", tags=["Trading"])

stock_repo = StockRepository()
dal = SupabaseDAL.get_instance()  # Keep this only for Saved Cards for now


# --- Models ---
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


# --- Routes ---


@router.post("/buy")
async def buy_stock(req: PurchaseRequest):
    print(f"💰 API: Processing buy request for {req.symbol}...")
    try:
        # 1. Securely save card (without ON CONFLICT)
        if req.save_card:
            # Check whether the user already has a saved card
            existing_card = (
                dal.table("saved_cards")
                .select("*")
                .eq("user_id", req.user_id)
                .execute()
            )

            card_data = {
                "user_id": req.user_id,
                "card_holder": req.card_holder,
                "card_number": req.card_number,
                "expiration": req.expiration,
                "cvv": req.cvv,
            }

            if existing_card.data and len(existing_card.data) > 0:
                # Update existing card
                dal.table("saved_cards").update(card_data).eq(
                    "user_id", req.user_id
                ).execute()
            else:
                # Insert new card
                dal.table("saved_cards").insert(card_data).execute()

        # 2. Execute the buy via the Repository
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
        print(f"❌ API Buy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sell")
async def sell_stock(req: SaleRequest):
    print(f"📉 API: Requesting sale for {req.symbol}")
    try:
        # --- Cleanup: a single call into the Repo ---
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
    # We can keep using `dal` here or move this into the Repo.
    # For the current cleanup, we focused on moving buy/sell into the Repo.
    response = (
        dal.table("saved_cards").select("*").eq("user_id", user_id).limit(1).execute()
    )
    return {"status": "success", "data": response.data[0] if response.data else None}
