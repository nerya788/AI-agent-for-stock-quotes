from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# העדכון כאן: אנחנו מייבאים מתוך התיקייה החדשה repository
from server.repository.stock_repository import StockRepository
app = FastAPI(title="Stock Quotes AI Agent Gateway")
repo = StockRepository()

# הגדרת מודל הנתונים לבקשה
class StockCreate(BaseModel):
    symbol: str
    price: float

@app.post("/stocks/watchlist")
async def add_stock(stock: StockCreate):
    """
    נקודת קצה המקבלת פקודת כתיבה ומנתבת אותה ל-Command Model [cite: 51]
    """
    try:
        result = repo.add_to_watchlist(stock.symbol, stock.price)
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)