from PySide6.QtWidgets import QMessageBox, QApplication
from client.modules.explorer.view.explorer_view import ExplorerView
from client.core.api_client import APIClient
import requests # נשתמש בזה לשמירה אם חסר ב-API Client

class ExplorerController:
    def __init__(self, app_controller):
        self.app = app_controller
        self.view = ExplorerView() # יצירת ה-View
        self.api = APIClient()
        
        self.setup_connections()

    def setup_connections(self):
        self.view.search_btn.clicked.connect(self.handle_search)
        self.view.ai_btn.clicked.connect(self.handle_ai)
        self.view.save_btn.clicked.connect(self.handle_save)
        self.view.back_btn.clicked.connect(self.handle_back)

    def handle_search(self):
        symbol = self.view.symbol_input.text().upper().strip()
        if not symbol: return

        self.view.info_label.setText("Fetching data...")
        
        # 1. קבלת מחיר
        data = self.api.get_live_quote(symbol)
        if data:
            self.view.info_label.setText(f"Stock: {data['symbol']} | Price: ${data['price']}")
            self.view.ai_btn.setEnabled(True)
            self.view.save_btn.setEnabled(True)
            
            # 2. קבלת היסטוריה לגרף (רשימת מחירים)
            history = self.api.get_stock_history(symbol)
            if history:
                # אנו צריכים רשימה של אובייקטים עם 'price', נניח שהשרת מחזיר מבנה כזה
                # השרת שלנו מחזיר {'prices': [...], 'dates': [...]}
                # נמיר את זה לפורמט שה-View מצפה לו
                prices = history.get('prices', [])
                formatted_data = [{'price': p} for p in prices] 
                self.view.plot_chart(symbol, formatted_data)
        else:
            self.view.info_label.setText("Stock not found.")

    def handle_ai(self):
        symbol = self.view.symbol_input.text().upper().strip()
        self.view.ai_result.setVisible(True)
        self.view.ai_result.setText("AI is thinking... 🤖")
        QApplication.processEvents()

        response = self.api.get_ai_analysis(symbol)
        analysis = response.get('analysis', 'No analysis available.')
        self.view.ai_result.setText(f"💡 AI Analysis:\n{analysis}")

    def handle_save(self):
        symbol = self.view.symbol_input.text().upper().strip()
        # שימוש ב-API Client או requests ישירות אם הפונקציה לא קיימת שם עדיין
        try:
            # אופציה א': אם הוספת ל-APIClient
            # self.api.add_to_watchlist(symbol)
            
            # אופציה ב': חיקוי הלוגיקה המקורית (כדי שיעבוד בטוח)
            resp = requests.post(f"http://127.0.0.1:8000/stocks/watchlist/auto?symbol={symbol}")
            
            if resp.status_code == 200:
                QMessageBox.information(self.view, "Success", f"Saved {symbol} to watchlist!")
            else:
                QMessageBox.warning(self.view, "Error", "Failed to save stock.")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Connection error: {e}")

    def handle_back(self):
        """חזרה לדשבורד דרך ה-AppController"""
        print("⬅️ Going back to Dashboard...")
        if hasattr(self.app, 'navigate_to_portfolio'):
            self.app.navigate_to_portfolio()