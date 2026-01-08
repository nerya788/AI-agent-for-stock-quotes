from fastapi import APIRouter, HTTPException
from server.services.stock_service import StockService
from server.services.ai_service import AIService
from server.repositories.stock_repository import StockRepository

# יצירת הראוטר (במקום app = FastAPI)
router = APIRouter(prefix="/stocks", tags=["Stocks"])

# אתחול השירותים (Dependency Injection)
stock_service = StockService()   # מביא נתונים (Gateway לשעבר)
ai_service = AIService()         # מנתח נתונים (Ollama)
stock_repo = StockRepository()   # שומר נתונים (Supabase)

# 1. קבלת מחיר מניה בזמן אמת
@router.get("/quote/{symbol}")
async def get_stock_price(symbol: str):
    data = stock_service.get_live_quote(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock symbol not found")
    return data

# 2. שמירה אוטומטית בדאטה-בייס (Command Model)
@router.post("/watchlist/auto")
async def add_live_stock_to_db(symbol: str):
    # שימוש ב-Service כדי להביא מחיר
    live_data = stock_service.get_live_quote(symbol)
    if not live_data:
        raise HTTPException(status_code=400, detail="Could not fetch live price")
    
    # שימוש ב-Repository כדי לשמור
    result = stock_repo.add_to_watchlist(live_data["symbol"], live_data["price"])
    return {"message": "Saved to cloud", "data": result.data}

# 3. היסטוריית מניות (עבור הגרפים)
@router.get("/history/{symbol}")
async def get_stock_history(symbol: str):
    history = stock_service.get_history(symbol)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

# 4. סוכן ה-AI
@router.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    # שלב א': הבאת המידע
    data = stock_service.get_live_quote(symbol)
    if not data:
        return {"analysis": "Could not fetch data for analysis."}

    # שלב ב': שליחה למוח של ה-AI (נמצא ב-services/ai_service.py)
    analysis = ai_service.analyze_stock(data['symbol'], data['price'])
    return {"analysis": analysis}