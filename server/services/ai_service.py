import os
import requests

from langchain_community.llms import Ollama

try:
    from huggingface_hub import InferenceClient
except ImportError:  # huggingface-hub אופציונלי
    InferenceClient = None

class AIService:
    def __init__(self):
        self.llm = None
        self.is_active = False
        self.hf_client = None
        self.hf_active = False
        # טוקן Hugging Face – תומך גם HF_TOKEN וגם HUGGINGFACEHUB_API_TOKEN
        self.hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        # מודל תרגום ברירת מחדל – יציב ונתמך ב-HF Inference API
        self.hf_translation_model = os.getenv(
            "HF_TRANSLATION_MODEL", "Helsinki-NLP/opus-mt-en-he"
        )
        
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

        # --- Hugging Face Inference API לדירוג חדשות ---
        try:
            if InferenceClient is not None:
                # מחזיקים client (גם לדרוג, גם לתרגום אם נרצה), אבל לדירוג נשתמש ב-HTTP ישיר
                self.hf_client = InferenceClient(
                    provider="hf-inference",
                    api_key=self.hf_token,
                ) if self.hf_token else None
                self.hf_active = bool(self.hf_token)
                if self.hf_active:
                    print("✅ HF Client initialized (token detected) for news AI features")
                else:
                    print("⚠️ HF token not set – news AI in MOCK mode")
            else:
                print("⚠️ huggingface-hub not installed. News ranking in MOCK mode.")
        except Exception as e:
            print(f"⚠️ HF Client init failed: {e}. News ranking in MOCK mode.")

    # --- עזר: ניקוי טקסט מתורגם מהקדמות מיותרות ---

    def _clean_translation_output(self, text: str) -> str:
        """מנקה מהתוצאה המתורגמת הקדמות כמו
        "translate English to Hebrew:" או "תרגום מאנגלית לעברית:" וכד'.

        מחזיר טקסט נקי להצגה למשתמש.
        """
        if not text:
            return text

        t = str(text).strip()
        # הסרות באנגלית (אם המודל הדפיס את הפרומפט עצמו)
        lower = t.lower()
        english_prefixes = [
            "translate english to hebrew:",
            "translation english to hebrew:",
            "english to hebrew:",
        ]
        for pref in english_prefixes:
            if lower.startswith(pref):
                t = t[len(pref) :].lstrip()
                lower = t.lower()

        # הסרות בעברית – וריאציות נפוצות
        hebrew_prefixes = [
            "תרגום מאנגלית לעברית",
            "תרגם מאנגלית לעברית",
        ]
        for pref in hebrew_prefixes:
            if t.startswith(pref):
                rest = t[len(pref) :].lstrip()
                if rest.startswith(":"):
                    rest = rest[1:].lstrip()
                t = rest
                break

        return t.strip()

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
    
    def generate_investment_plan(self, prompt: str) -> str:
        """
        יצירת תכנית השקעה מותאמת אישית באמצעות AI
        """
        # אם אין מודל אמיתי, נחזיר תוכנית דמה
        if not self.is_active or not self.llm:
            return """
📊 INVESTMENT PLAN - Based on Your Profile

🎯 Top 5 Stock Recommendations:
1. NVDA (40%) - Nvidia - Strong tech growth, high dividend potential
2. AAPL (25%) - Apple - Stable blue-chip, defensive position
3. JNJ (20%) - Johnson & Johnson - Dividend stock, low risk
4. MSFT (10%) - Microsoft - Cloud growth exposure
5. Cash Reserve (5%) - Liquidity buffer for short-term opportunities

📈 Expected Performance:
- Annual Return Projection: 6-8% (Conservative approach)
- Risk Level: Low-Medium
- Volatility Index: Moderate

⏰ Implementation Timeline:
Week 1: Allocate 50% of capital
Week 2-3: Allocate remaining 50%
Monitor quarterly, rebalance annually

✅ Diversification Score: 85% - Well-balanced across sectors
🛡️ Risk Assessment: CONSERVATIVE - Suitable for your profile
            """
        
        # ניסיון פנייה למודל האמיתי (אם Ollama רץ)
        try:
            print(f"🤖 AI Service: Generating investment plan with Llama3...")
            response = self.llm.invoke(prompt)
            return str(response).strip()
        except Exception as e:
            print(f"❌ AI Error: {e}")
            print(f"⚠️ Falling back to mock mode...")
            return """
📊 INVESTMENT PLAN - MOCK MODE (AI Unavailable)

🎯 Top 5 Stock Recommendations:
1. NVDA (40%) - Nvidia - Strong tech growth
2. AAPL (25%) - Apple - Stable blue-chip
3. JNJ (20%) - Johnson & Johnson - Dividend stock
4. MSFT (10%) - Microsoft - Cloud growth
5. Cash Reserve (5%) - Liquidity buffer

📈 Expected Performance:
- Annual Return: 6-8%
- Risk Level: Low-Medium
- Diversification: 85%

⚠️ Note: This is a mock analysis. Ensure Ollama is running for real AI recommendations.
            """

    def rank_news_for_stock(self, symbol: str, news_items: list[dict]) -> list[dict]:
        """דירוג חדשות לפי חשיבות עבור מניה מסוימת.

        news_items: רשימה של אובייקטים עם המפתחות: title, summary, url, published_at
        מחזיר: אותה רשימה, עם שדה importance_score וממויינת מהכי חשוב לפחות חשוב.
        """

        # מצב MOCK – אם HF לא זמין/אין טוקן, נבצע דירוג פשוט לפי אורך הטקסט
        if not self.hf_active or not getattr(self, "self.hf_token", None):
            ranked = []
            for item in news_items:
                text = f"{item.get('title', '')}. {item.get('summary', '')}"
                score = min(len(text) / 400.0, 1.0)  # הערכה גסה בין 0 ל-1
                enriched = dict(item)
                enriched["importance_score"] = round(float(score), 3)
                ranked.append(enriched)

            ranked.sort(key=lambda x: x["importance_score"], reverse=True)
            return ranked

        ranked_items: list[dict] = []

        api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        labels = ["very important", "somewhat important", "not important"]

        for item in news_items:
            text = f"[Ticker: {symbol.upper()}] {item.get('title', '')}. {item.get('summary', '')}".strip()
            if not text:
                continue

            try:
                resp = requests.post(
                    api_url,
                    headers=headers,
                    json={
                        "inputs": text,
                        "parameters": {
                            "candidate_labels": labels,
                            "multi_label": False,
                        },
                    },
                    timeout=25,
                )
                if resp.status_code != 200:
                    raise ValueError(f"status={resp.status_code}, body={resp.text[:100]}")

                data = resp.json()
                label_scores: dict[str, float] = {}
                if isinstance(data, dict) and "labels" in data and "scores" in data:
                    for lbl, sc in zip(data["labels"], data["scores"]):
                        label_scores[lbl] = float(sc)
                else:
                    raise ValueError("Unexpected HF zero-shot result format")

                score = (
                    1.0 * label_scores.get("very important", 0.0)
                    + 0.6 * label_scores.get("somewhat important", 0.0)
                    + 0.1 * label_scores.get("not important", 0.0)
                )

            except Exception as e:
                print(f"⚠️ HF ranking failed for news item: {e}")
                # fallback במקרה של שגיאה: דירוג פשוט לפי אורך הטקסט
                score = min(len(text) / 400.0, 1.0)

            enriched = dict(item)
            enriched["importance_score"] = round(float(score), 3)
            ranked_items.append(enriched)

        ranked_items.sort(key=lambda x: x["importance_score"], reverse=True)
        return ranked_items

    # --- תרגום לעברית באמצעות Hugging Face ---

    def _translate_text_to_hebrew(self, text: str) -> str:
        """תרגום טקסט מאנגלית לעברית דרך Hugging Face Inference API.

        במקרה של כשל או חוסר טוקן – מחזיר את הטקסט המקורי.
        """
        text = (text or "").strip()
        if not text:
            return text

        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not token:
            return text

        url = f"https://api-inference.huggingface.co/models/{self.hf_translation_model}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = requests.post(url, headers=headers, json={"inputs": text}, timeout=20)
            if resp.status_code != 200:
                print(
                    f"⚠️ HF translation error: status={resp.status_code}, body={resp.text[:120]}"
                )
                return text

            data = resp.json()
            # פורמט טיפוסי: [{"translation_text": "..."}]
            if isinstance(data, list) and data and "translation_text" in data[0]:
                return self._clean_translation_output(data[0]["translation_text"])
            # fallback לפורמטים אחרים
            if isinstance(data, dict) and "generated_text" in data:
                return self._clean_translation_output(data["generated_text"])
        except Exception as e:
            print(f"⚠️ HF translation exception: {e}")

        return text

    def translate_news_items_to_hebrew(self, news_items: list[dict]) -> list[dict]:
        """הוספת שדות title_he ו-summary_he לכל אייטם חדשות.

        ממומש בבאץ' אחד לטייטלים ובאץ' אחד לסיכומים כדי למנוע
        עשרות קריאות HTTP נפרדות (שעלולות "לתקוע" את האפליקציה).
        """
        if not news_items:
            return []

        # מתרגמים רק את מה שבאמת מציגים (עד 10 אייטמים)
        limited_items = news_items[:10]

        titles = [(item.get("title") or "").strip() for item in limited_items]
        summaries = [(item.get("summary") or "").strip() for item in limited_items]

        titles_he = self._translate_batch_to_hebrew(titles)
        summaries_he = self._translate_batch_to_hebrew(summaries)

        translated: list[dict] = []
        for idx, item in enumerate(limited_items):
            copy = dict(item)
            copy["title_he"] = titles_he[idx] if idx < len(titles_he) else titles[idx]
            copy["summary_he"] = (
                summaries_he[idx] if idx < len(summaries_he) else summaries[idx]
            )
            translated.append(copy)

        # אם היו יותר מ-10 אייטמים, נוסיף אותם ללא תרגום (לא מוצגים בפועל ב-UI)
        if len(news_items) > len(limited_items):
            for extra in news_items[len(limited_items) :]:
                translated.append(dict(extra))

        return translated

    def _translate_batch_to_hebrew(self, texts: list[str]) -> list[str]:
        """תרגום רשימת טקסטים לעברית באמצעות InferenceClient.translation.

        משתמש במודל טקסט-לטקסט (למשל google-t5/t5-base) עם פרומפט
        "translate English to Hebrew: ...". במקרה של כשל – נחזיר את הטקסטים המקוריים.
        """

        cleaned = [(t or "").strip() for t in texts]
        if not any(cleaned):
            return cleaned

        if InferenceClient is None or not self.hf_token:
            return cleaned

        try:
            client = InferenceClient(provider="hf-inference", api_key=self.hf_token)
        except Exception as e:
            print(f"⚠️ HF translation client init failed: {e}")
            return cleaned

        results: list[str] = []
        for idx, text in enumerate(cleaned):
            if not text:
                results.append("")
                continue
            try:
                prompt = f"translate English to Hebrew: {text}"
                out = client.translation(prompt, model=self.hf_translation_model)
                if isinstance(out, str):
                    translated = out
                elif isinstance(out, dict) and "translation_text" in out:
                    translated = out["translation_text"]
                elif isinstance(out, list) and out and isinstance(out[0], dict):
                    translated = out[0].get("translation_text") or out[0].get(
                        "generated_text", ""
                    )
                else:
                    translated = text

                results.append(self._clean_translation_output(translated))
            except Exception as e:
                print(f"⚠️ HF single translation failed (idx={idx}): {e}")
                results.append(text)

        return results