import yfinance as yf

class StockGateway:
    """
    Free API Gateway using yfinance (No API key required).
    """
    def get_live_quote(self, symbol: str):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.fast_info
            return {
                "symbol": symbol.upper(),
                "price": round(data['last_price'], 2),
                "currency": "USD"
            }
        except Exception as e:
            return {"error": f"Could not fetch data for {symbol}: {str(e)}"}