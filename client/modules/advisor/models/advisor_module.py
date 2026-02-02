class AdvisorModel:
    def __init__(self, symbol: str, analysis_text: str):
        self.symbol = symbol
        self.analysis_text = analysis_text

    @classmethod
    def from_json(cls, symbol, data: dict):
        return cls(
            symbol=symbol,
            analysis_text=data.get("analysis", "No analysis provided.")
        )