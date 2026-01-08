from langchain_community.llms import Ollama

class AIService:
    def __init__(self):
        self.llm = None
        self.is_active = False
        
        # ניסיון טעינה "בטוח" - לא יפיל את השרת אם הספרייה לא מותקנת
        try:
            # מנסים לייבא רק אם קיים
            from langchain_ollama import OllamaLLM
            self.llm = OllamaLLM(model="llama3")
            self.is_active = True
            print("✅ AI Service initialized (Ready to connect to Docker/Local Ollama)")
            
        except ImportError:
            print("⚠️ langchain-ollama not installed. AI Service running in MOCK mode.")
        except Exception as e:
            print(f"⚠️ AI Service warning: {e}. Running in MOCK mode.")

    def analyze_stock(self, symbol: str, price: float) -> str:
        # אם אין לנו מודל אמיתי, נחזיר תשובת דמה
        if not self.is_active or not self.llm:
            return (f"[MOCK Analysis] The AI service is currently optimized via Docker. "
                    f"Mock insight: {symbol} at ${price} shows stable trends. "
                    f"Consider market volatility before investing.")

        # ניסיון פנייה למודל האמיתי (אם הוא מותקן)
        try:
            prompt = f"Analyze the stock {symbol} at {price} USD. Is it risky? Answer in 2 short sentences."
            return self.llm.invoke(prompt)
        except Exception as e:
            print(f"❌ Connection to Ollama failed: {e}")
            return "AI Service is offline. Please check your Docker container."