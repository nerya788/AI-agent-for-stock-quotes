from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.models.agent_dto import AgentResponse
from server.services.stock_service import StockService
from server.services.ai_service import AIService
from server.services.news_service import NewsService
from server.repositories.stock_repository import StockRepository
from server.dal.supabase_client import SupabaseDAL
from datetime import datetime
from server.services.agent_service import AgentService

router = APIRouter(prefix="/stocks", tags=["Stocks"])

# אתחול השירותים
stock_service = StockService()
ai_service = AIService()
news_service = NewsService()
agent_service = AgentService()
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


class NewsItem(BaseModel):
    title: str
    summary: str | None = None
    url: str | None = None
    published_at: str | None = None


class NewsRankingRequest(BaseModel):
    symbol: str
    news: list[NewsItem]


class ChatRequest(BaseModel):
    message: str
    user_id: str

@router.post("/agent/chat", response_model=AgentResponse)
async def chat_with_agent(request: ChatRequest):
    return agent_service.process_request(request.message, request.user_id)

# --- 1. התיקון המקצועי לדשבורד ---
@router.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str):
    print(f"📊 API Layer: Requesting watchlist for user {user_id}")
    try:
        # במקום לפנות ל-dal, פונים ל-Repository
        response = stock_repo.get_watchlist(user_id)

        # ה-Repository מחזיר לנו אובייקט של Supabase, אנחנו מוציאים את ה-data
        return {"status": "success", "data": response.data if response.data else []}

    except Exception as e:
        print(f"❌ API Layer Error: {e}")
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
    print(f"✅ API Layer: Recording event {event.event_type} for {event.symbol}")
    try:
        # במקום ה-dal.table(...).insert הישן, משתמשים ב-Repo:
        response = stock_repo.record_event(
            symbol=event.symbol,
            event_type=event.event_type,
            payload=event.payload,
            user_id=event.user_id,
        )

        if response.data:
            return {"success": True, "data": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail="Failed to save event")

    except Exception as e:
        print(f"❌ API Layer Error: {e}")
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


@router.get("/news/{symbol}")
async def get_ranked_news_for_symbol(symbol: str):
    print(f"\n📡 DEBUG ROUTE: Fetching & Ranking news for {symbol}")
    try:
        # 1. מביאים חדשות
        raw_news = news_service.get_company_news(symbol)
        
        # 2. שולחים לדירוג (ה-AI Service כבר מוגבל ל-10 כתבות כדי שיהיה מהיר)
        ranked_news = ai_service.rank_news_for_stock(symbol, raw_news)
        
        print("📡 DEBUG ROUTE: Finished Ranking")
        return {"symbol": symbol.upper(), "news": ranked_news}

    except Exception as e:
        print(f"❌ DEBUG ROUTE ERROR: {e}")
        return {"symbol": symbol.upper(), "news": []}


@router.post("/news/rank")
async def rank_news(request: NewsRankingRequest):
    """דירוג פיד חדשות למניה לפי חשיבות, באמצעות Hugging Face (או MOCK fallback).

    ה-client יכול להביא חדשות מכל API חיצוני, לשלוח אלינו רשימת ידיעות,
    ולקבל בחזרה את אותן ידיעות עם שדה importance_score וממויין מהכי חשוב לפחות חשוב.
    """
    try:
        raw_items = [item.model_dump() for item in request.news]
        ranked = ai_service.rank_news_for_stock(request.symbol, raw_items)
        return {"symbol": request.symbol.upper(), "news": ranked}
    except Exception as e:
        print(f"❌ Error ranking news: {e}")
        raise HTTPException(status_code=500, detail="Failed to rank news items")


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
