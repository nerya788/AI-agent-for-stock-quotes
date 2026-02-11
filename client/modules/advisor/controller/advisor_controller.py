from PySide6.QtWidgets import QApplication
from client.modules.advisor.view.advisor_view import AdvisorView
from client.modules.advisor.models.advisor_module import AdvisorModel
from client.core.api_client import APIClient
from client.core.worker_thread import WorkerThread  # <--- ייבוא המנוע


class AdvisorController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = AdvisorView()
        self.api = APIClient()
        self.worker = None  # משתנה לשמירת התהליכון

        self.setup_connections()

    def setup_connections(self):
        self.view.analyze_btn.clicked.connect(self.handle_analysis)

    # --- פונקציית רקע (העבודה השחורה) ---
    def _analysis_task(self, symbol):
        """מבצע את הפנייה ל-API ברקע"""
        return self.api.get_ai_analysis(symbol)

    # --- הנדלר ראשי ---
    def handle_analysis(self):
        symbol = self.view.symbol_input.text().upper().strip()
        if not symbol: return

        # עדכון UI: מראה שהמערכת עובדת, אבל לא תוקע אותה!
        self.view.result_area.setText(f"🤔 AI is analyzing {symbol}... (Feel free to move the window!)")
        self.view.analyze_btn.setEnabled(False)

        # יצירת והפעלת התהליכון
        self.worker = WorkerThread(self._analysis_task, symbol)
        self.worker.finished.connect(self.on_analysis_ready)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_analysis_ready(self, response):
        """נקרא אוטומטית כשהתשובה מגיעה מהשרת"""
        self.view.analyze_btn.setEnabled(True)

        try:
            symbol = self.view.symbol_input.text().upper().strip()

            # יצירת מודל מהתשובה (כמו בקוד המקורי שלך)
            model = AdvisorModel.from_json(symbol, response)

            # עדכון הטקסט במסך
            self.view.result_area.setText(f"💡 Analysis for {model.symbol}:\n\n{model.analysis_text}")

        except Exception as e:
            self.view.result_area.setText(f"❌ Error processing data: {str(e)}")

    def on_error(self, error_msg):
        """טיפול בשגיאות חיבור"""
        self.view.analyze_btn.setEnabled(True)
        self.view.result_area.setText(f"❌ Connection Error: {error_msg}")