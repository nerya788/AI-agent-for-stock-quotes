from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.stock_service import StockService
from server.services.ai_service import AIService
from server.repositories.stock_repository import StockRepository

# יצירת הראוטר (במקום app = FastAPI)
router = APIRouter(prefix="/stocks", tags=["Stocks"])

# אתחול השירותים (Dependency Injection)
stock_service = StockService()   # מביא נתונים (Gateway לשעבר)
ai_service = AIService()         # מנתח נתונים (Ollama)
stock_repo = StockRepository()   # שומר נתונים (Supabase)

# מודל לבקשת תכנית השקעה
class InvestmentPlanRequest(BaseModel):
    amount: str
    sector: str
    risk: str
    availability: str
    location: str

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

@router.get("/watchlist")
def get_watchlist():
    """
    שליפת תיק ההשקעות של המשתמש
    """
    try:
        response = stock_repo.get_watchlist()
        # ב-Supabase התשובה מגיעה בתוך .data
        return response.data if hasattr(response, 'data') else response
    except Exception as e:
        print(f"Error fetching watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# 5. תכנית השקעה מותאמת אישית
@router.post("/ai-investment-plan")
async def generate_investment_plan(request: InvestmentPlanRequest):
    """
    סוכן AI ליצירת תכנית השקעה מותאמת
    """
    print(f"📊 Stock Routes: Generating investment plan...")
    print(f"   Amount: ${request.amount}")
    print(f"   Sector: {request.sector}")
    print(f"   Risk: {request.risk}")
    
    try:
        # בניית ה-prompt לAI
        prompt = f"""
You are a professional investment advisor. Based on the following client profile, provide a detailed investment plan:

Client Profile:
- Investment Amount: ${request.amount}
- Preferred Sector: {request.sector}
- Risk Tolerance: {request.risk}
- Investment Availability: {request.availability}
- Market Focus: {request.location}

Please provide:
1. Top 5 stock recommendations (with allocation percentages)
2. Risk assessment and expected returns
3. Diversification strategy
4. Implementation timeline

Format your response clearly with sections and bullet points.
        """
        
        # שליחה ל-AI Service
        recommendation = ai_service.generate_investment_plan(prompt)
        
        print(f"✅ Investment plan generated")
        return {"recommendation": recommendation}
        
    except Exception as e:
        print(f"❌ Error generating investment plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")