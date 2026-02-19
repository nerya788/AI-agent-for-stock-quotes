import requests
from langchain.tools import tool
from server.repositories.stock_repository import StockRepository
from server.services.stock_service import StockService

stock_repo = StockRepository()
stock_service = StockService()

def search_ticker_symbol(company_name: str) -> str:
    """
    פונקציית עזר (לא כלי ל-AI) שמחפשת סימול לפי שם חברה
    משתמשת ב-API ההשלמה האוטומטית של יאהו
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company_name}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            if "quotes" in data and len(data["quotes"]) > 0:
                # מחזיר את התוצאה הראשונה שהיא מניה (Equity)
                return data["quotes"][0]["symbol"]
    except Exception as e:
        print(f"Ticker search failed: {e}")
    
    return None

@tool
def get_stock_price(symbol: str) -> str:
    """Use this to get the current live price of a stock. Input is the ticker symbol (e.g., AAPL) or company name."""
    
    # ניקוי בסיסי
    clean_input = symbol.strip().upper().replace(".", "")
    
    # 1. ניסיון שליפה ישיר (אולי זה כבר סימול תקין?)
    quote = stock_service.get_live_quote(clean_input)
    
    # 2. אם לא מצאנו, ננסה לחפש את הסימול באינטרנט (הקסם קורה כאן!)
    if not quote:
        print(f"🕵️‍♂️ Direct lookup failed for '{clean_input}', searching Yahoo...")
        found_symbol = search_ticker_symbol(clean_input)
        
        if found_symbol:
            print(f"✅ Found symbol '{found_symbol}' for '{clean_input}'")
            quote = stock_service.get_live_quote(found_symbol)

    # 3. החזרת תשובה
    if quote:
        return f"The current price of {quote['symbol']} is ${quote['price']}."
    
    return f"Error: I couldn't find a stock named '{symbol}'. Please try providing the exact ticker symbol."

@tool
def check_my_portfolio(user_id: str) -> str:
    """Use this to see what stocks the specific user currently owns. Requires user_id."""
    if "user_id" in user_id.lower() and len(user_id) < 10:
        return "Error: You didn't provide the real User ID UUID."

    res = stock_repo.get_watchlist(user_id)
    if not res.data:
        return "The portfolio is currently empty."
    
    summary = "Current Portfolio:\n"
    for s in res.data:
        summary += f"- {s['symbol']}: {s['amount']} shares (Avg Buy Price: ${s['price']})\n"
    return summary

@tool
def identify_intent(user_input: str) -> str:
    """This is a helper tool to identify user intent. Not meant to be called directly by the agent."""
    text = user_input.lower()
    if any(word in text for word in ["buy", "sell", "trade"]):
        return "TRADING"
    if any(word in text for word in ["plan", "offer", "advise", "suggestion", "recommend", "advice"]):
        return "INVESTMENT_ADVICE"
    return "CHAT"