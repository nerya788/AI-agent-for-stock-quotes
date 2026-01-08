import yfinance as yf

# התיקון: שינוי השם מ-StockGateway ל-StockService
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
                
            price = data['Close'].iloc[-1]
            
            return {
                "symbol": symbol.upper(),
                "price": round(float(price), 2),
                "currency": "USD",
                "source": "Yahoo Finance (Service Layer)"
            }
        except Exception as e:
            print(f"❌ Error in StockService: {e}")
            return None

    @staticmethod
    def get_history(symbol: str):
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo") # חודש אחרון
            if hist.empty:
                return None
            
            # המרה לפורמט נוח לגרף
            return {
                "symbol": symbol,
                "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                "prices": hist['Close'].tolist()
            }
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
            return None