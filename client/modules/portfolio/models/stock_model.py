class StockModel:
    def __init__(self, symbol: str, price: float, change_percent: float = 0.0):
        self.symbol = symbol
        self.price = price
        self.change_percent = change_percent

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            symbol=data.get("symbol"),
            price=data.get("price"),
            change_percent=data.get("change_percent", 0.0)
        )