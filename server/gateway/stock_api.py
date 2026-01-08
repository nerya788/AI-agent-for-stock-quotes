import os
import certifi
import yfinance as yf

# Global solution for SSL issue
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

class StockGateway:
    @staticmethod
    def get_live_quote(symbol: str):
        """
        API Gateway: Calling external service to get stock data
        """
        try:
            print(f"🔄 Requesting external service for: {symbol}...")
            
            # We do not manually define a Session, letting yfinance manage it
            stock = yf.Ticker(symbol)
            
            # Fetching history for the last day
            data = stock.history(period="1d")
            
            if data.empty:
                print(f"⚠️ No data found for {symbol}")
                return None
                
            price = data['Close'].iloc[-1]
            
            return {
                "symbol": symbol.upper(),
                "price": round(float(price), 2),
                "currency": "USD",
                "source": "Yahoo Finance (Global SSL Fix)"
            }
        except Exception as e:
            print(f"❌ Gateway error: {e}")
            return None

    @staticmethod
    def get_history(symbol: str, period="1mo"):
        """
        New function for UI Graph: Fetches historical data.
        """
        try:
            stock = yf.Ticker(symbol)
            # Fetch history
            hist = stock.history(period=period)

            if hist.empty:
                return []

            # Convert to list of dictionaries for the JSON response
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "price": round(float(row['Close']), 2)
                })
            return data
        except Exception as e:
            print(f"❌ History error: {e}")
            return []