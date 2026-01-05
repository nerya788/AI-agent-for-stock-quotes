from fastapi import FastAPI, HTTPException
from server.gateway.stock_api import StockGateway
from server.repository.stock_repository import StockRepository
from pydantic import BaseModel

app = FastAPI(title="Stock Quotes AI Agent Gateway")
repo = StockRepository()
stock_gw = StockGateway()

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Stock Quotes AI Agent API",
        "status": "Online",
        "documentation": "/docs"
    }

@app.get("/stocks/quote/{symbol}")
async def get_stock_price(symbol: str):
    """
    Query Model: Fetches live stock price using the Gateway.
    """
    data = stock_gw.get_live_quote(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Stock symbol not found or service unavailable")
    return data

@app.post("/stocks/watchlist/auto")
async def add_live_stock_to_db(symbol: str):
    """
    Combination of Gateway and Command Model: 
    Fetches live price and automatically saves it to the cloud.
    """
    live_data = stock_gw.get_live_quote(symbol)
    if not live_data:
        raise HTTPException(status_code=400, detail="Could not fetch live price")
    
    result = repo.add_to_watchlist(live_data["symbol"], live_data["price"])
    return {"message": "Saved to cloud", "data": result.data}