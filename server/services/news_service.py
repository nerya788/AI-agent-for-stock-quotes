import os
from datetime import date, timedelta
from typing import List, Dict

import httpx


class NewsService:
    """Service for fetching financial news from Finnhub.

    Relies on FINNHUB_API_KEY being set in the .env file.
    Returns news in a normalized format compatible with AIService.rank_news_for_stock.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self) -> None:
        self.api_key = os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            print(
                "⚠️ FINNHUB_API_KEY not set – NewsService will operate in empty/mock mode"
            )

    def get_company_news(self, symbol: str, days_back: int = 10) -> List[Dict]:
        """Fetch company news for the last X days (default: 10).

        Returns a list of dicts with keys:
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
                # Detailed log to help debugging
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
