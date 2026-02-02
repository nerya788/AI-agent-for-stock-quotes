class ChartModel:
    def __init__(self, symbol: str, dates: list, prices: list):
        self.symbol = symbol
        self.dates = dates
        self.prices = prices

    @classmethod
    def from_json(cls, data: dict):
        """ממיר את תשובת ה-Service/API לאובייקט מודל"""
        return cls(
            symbol=data.get("symbol", ""),
            dates=data.get("dates", []),
            prices=data.get("prices", [])
        )