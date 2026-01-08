from fastapi import FastAPI, HTTPException
from server.gateway.stock_api import StockGateway
from server.repository.stock_repository import StockRepository
from langchain_community.llms import Ollama
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

@app.get("/stocks/history/{symbol}")
async def get_stock_history(symbol: str):
    """
    Returns historical data for the graph
    """
    history = stock_gw.get_history(symbol)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history


@app.get("/stocks/analyze/{symbol}")
async def analyze_stock(symbol: str):
    """
    AI Agent: Uses Ollama (LLM) to analyze the stock
    """
    try:
        # 1. Get data
        data = stock_gw.get_live_quote(symbol)
        if not data:
            return {"analysis": "Could not fetch data for analysis."}

        # 2. Define the prompt
        prompt = f"Analyze the stock {data['symbol']} at {data['price']} USD. Is it risky? Answer in 2 short sentences."

        # 3. Call Ollama
        try:
            llm = Ollama(model="llama3")
            response = llm.invoke(prompt)
            return {"analysis": response}
        except:
            return {
                "analysis": "AI Service unavailable (Check if Ollama is running). Mock analysis: Market looks volatile, proceed with caution."}

    except Exception as e:
        return {"analysis": f"Error: {str(e)}"}