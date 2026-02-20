import yfinance as yf


# Fix: rename from StockGateway to StockService
class StockService:
    @staticmethod
    def get_live_quote(symbol: str):
        try:
            print(f"🔄 Service: Fetching live quote for {symbol}...")
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")

            if data.empty:
                print(f"⚠️ No data found for {symbol}")
                return None

            price = data["Close"].iloc[-1]

            return {
                "symbol": symbol.upper(),
                "price": round(float(price), 2),
                "currency": "USD",
                "source": "Yahoo Finance (Service Layer)",
            }
        except Exception as e:
            print(f"❌ Error in StockService: {e}")
            return None

    @staticmethod
    def get_history(symbol: str):
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo")  # Last month
            if hist.empty:
                return None

            # Convert to a chart-friendly format
            return {
                "symbol": symbol,
                "dates": hist.index.strftime("%Y-%m-%d").tolist(),
                "prices": hist["Close"].tolist(),
            }
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
            return None

    def get_company_info(self, symbol: str):
        """Fetch general company info (including sector)."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "longBusinessSummary": info.get("longBusinessSummary", ""),
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return {"sector": "Unknown"}
