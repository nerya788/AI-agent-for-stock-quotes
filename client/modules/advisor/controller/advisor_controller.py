from PySide6.QtWidgets import QApplication
from client.modules.advisor.view.advisor_view import AdvisorView
from client.modules.advisor.models.advisor_module import AdvisorModel
from client.core.api_client import APIClient

class AdvisorController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = AdvisorView()
        self.api = APIClient()
        
        self.setup_connections()

    def setup_connections(self):
        self.view.analyze_btn.clicked.connect(self.handle_analysis)

    def handle_analysis(self):
        symbol = self.view.symbol_input.text().upper().strip()
        if not symbol: return

        # UI Update
        self.view.result_area.setText(f"🤔 AI is analyzing {symbol}...")
        self.view.analyze_btn.setEnabled(False)
        QApplication.processEvents()

        try:
            # שימוש ב-API
            response = self.api.get_ai_analysis(symbol)
            
            # יצירת מודל ועדכון תצוגה
            model = AdvisorModel.from_json(symbol, response)
            self.view.result_area.setText(f"💡 Analysis for {model.symbol}:\n\n{model.analysis_text}")

        except Exception as e:
            self.view.result_area.setText(f"❌ Error: {str(e)}")
        
        finally:
            self.view.analyze_btn.setEnabled(True)