from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.stock_service import StockService
from server.services.ai_service import AIService
from server.repositories.stock_repository import StockRepository
from server.dal.supabase_client import SupabaseDAL
from datetime import datetime

router = APIRouter(prefix="/stocks", tags=["Stocks"])

# אתחול השירותים
stock_service = StockService()
ai_service = AIService()
stock_repo = StockRepository()
dal = SupabaseDAL.get_instance()


# מודלים
class StockEventRequest(BaseModel):
    user_id: str
    symbol: str
    event_type: str
    payload: dict = {}


class InvestmentPlanRequest(BaseModel):
    amount: str
    sector: str
    risk: str
    availability: str
    location: str


# --- 1. התיקון הקריטי לדשבורד (Watchlist לפי User ID) ---
@router.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str):
    """
    מחזיר את התיק הנוכחי (Watchlist) של המשתמש הספציפי
    """
    print(f"📊 Serving watchlist for user: {user_id}")
    try:
        # שליפה ישירה מהטבלה stocks_watchlist לפי user_id
        response = (
            dal.table("stocks_watchlist").select("*").eq("user_id", user_id).execute()
        )

        data = response.data if response.data else []
        print(f"✅ Found {len(data)} items in watchlist.")
        return {"status": "success", "data": data}

    except Exception as e:
        print(f"❌ Error fetching watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- כל שאר הפונקציות המקוריות שלך נשארות כאן ---


@router.get("/quote/{symbol}")
async def get_stock_price(symbol: str):
    data = stock_service.get_live_quote(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock symbol not found")
    return data


@router.get("/popular")
async def get_popular_stocks():
    try:
        popular = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "AMZN", "name": "Amazon.com, Inc."},
            {"symbol": "GOOGL", "name": "Alphabet Inc. Class A"},
            {"symbol": "META", "name": "Meta Platforms, Inc."},
            {"symbol": "TSLA", "name": "Tesla, Inc."},
            {"symbol": "AVGO", "name": "Broadcom Inc."},
            {"symbol": "NFLX", "name": "Netflix, Inc."},
            {"symbol": "AMD", "name": "Advanced Micro Devices, Inc."},
            {"symbol": "CRM", "name": "Salesforce, Inc."},
            {"symbol": "ORCL", "name": "Oracle Corporation"},
            {"symbol": "ADBE", "name": "Adobe Inc."},
            {"symbol": "INTC", "name": "Intel Corporation"},
            {"symbol": "QCOM", "name": "Qualcomm Incorporated"},
            {"symbol": "CSCO", "name": "Cisco Systems, Inc."},
            {"symbol": "PEP", "name": "PepsiCo, Inc."},
            {"symbol": "COST", "name": "Costco Wholesale Corporation"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
            {"symbol": "KO", "name": "The Coca-Cola Company"},
        ]

        enriched = []
        for stock in popular:
            quote = stock_service.get_live_quote(stock["symbol"])
            if quote:
                enriched.append(
                    {
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "price": quote.get("price"),
                    }
                )
            else:
                enriched.append(
                    {"symbol": stock["symbol"], "name": stock["name"], "price": None}
                )

        return {"stocks": enriched}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event")
async def record_stock_event(event: StockEventRequest):
    try:
        data = {
            "user_id": event.user_id,
            "symbol": event.symbol.upper(),
            "event_type": event.event_type,
            "payload": event.payload,
            "created_at": datetime.utcnow().isoformat(),
        }

        response = dal.table("stock_events").insert(data).execute()

        if response.data:
            print(f"✅ Stock event saved: {event.symbol} for user {event.user_id}")
            return {"success": True, "data": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Failed to save event")

    except Exception as e:
        print(f"❌ Error saving stock event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{symbol}")
async def get_stock_history(symbol: str):
    history = stock_service.get_history(symbol)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history


@router.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    data = stock_service.get_live_quote(symbol)
    if not data:
        return {"analysis": "Could not fetch data for analysis."}
    analysis = ai_service.analyze_stock(data["symbol"], data["price"])
    return {"analysis": analysis}


@router.get("/user-purchases/{user_id}")
async def get_user_purchases(user_id: str):
    return {"status": "deprecated", "data": []}


@router.post("/ai-investment-plan")
async def generate_investment_plan(request: InvestmentPlanRequest):
    print(f"📊 Stock Routes: Generating investment plan...")
    try:
        prompt = f"""
        Client Profile:
        - Investment Amount: ${request.amount}
        - Preferred Sector: {request.sector}
        - Risk Tolerance: {request.risk}
        - Investment Availability: {request.availability}
        - Market Focus: {request.location}

        Please provide:
        1. Top 5 stock recommendations
        2. Risk assessment
        3. Implementation timeline
        """
        recommendation = ai_service.generate_investment_plan(prompt)
        print(f"✅ Investment plan generated")
        return {"recommendation": recommendation}

    except Exception as e:
        print(f"❌ Error generating investment plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.get("/info/{symbol}")
def get_stock_info(symbol: str):
    return stock_service.get_company_info(symbol)
