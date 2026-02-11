import os
from datetime import date, timedelta
from typing import List, Dict

import httpx


class NewsService:
    """שירות למשיכת חדשות פיננסיות מ-Finnhub.

    מסתמך על FINNHUB_API_KEY שמוגדר בקובץ .env.
    מחזיר חדשות בפורמט אחיד שמתאים ל-AIService.rank_news_for_stock.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self) -> None:
        self.api_key = os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            print("⚠️ FINNHUB_API_KEY not set – NewsService will operate in empty/mock mode")

    def get_company_news(self, symbol: str, days_back: int = 10) -> List[Dict]:
        """שליפת חדשות עבור מניה מסוימת אחרונה X ימים (ברירת מחדל 10 ימים).

        מחזיר רשימת מילונים עם המפתחות:
        - title
        - summary
        - url
        - published_at
        """
        if not self.api_key:
            return []

        to_date = date.today()
        from_date = to_date - timedelta(days=days_back)

        params = {
            "symbol": symbol.upper(),
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "token": self.api_key,
        }

        url = f"{self.BASE_URL}/company-news"
        try:
            resp = httpx.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                # לוג מפורט לעזרת דיבוג (למשתמש)
                print(
                    f"❌ Finnhub company-news error for {symbol}: "
                    f"status={resp.status_code}, body={resp.text[:200]}"
                )
                return []

            data = resp.json() or []
        except Exception as e:
            print(f"❌ Error fetching Finnhub news for {symbol}: {e}")
            return []

        normalized: List[Dict] = []
        for item in data:
            normalized.append(
                {
                    "title": item.get("headline", ""),
                    "summary": item.get("summary", ""),
                    "url": item.get("url"),
                    "published_at": str(item.get("datetime")),
                }
            )

        return normalized
