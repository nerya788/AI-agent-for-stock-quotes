from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
    QTableWidgetItem,
    QPushButton,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import requests

# ייבוא ה-Views
from client.modules.portfolio.view.dashboard_view import DashboardView
from client.modules.portfolio.view.investment_view import InvestmentView
from client.modules.trade.controller.trade_controller import TradeController
from client.core.api_client import APIClient
from client.core.worker_thread import WorkerThread  # <--- הוספנו את המנוע!


# from client.modules.portfolio.view.stock_search_dialog import StockSearchDialog

class PortfolioController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.api = APIClient()
        self.stocks_data = {}  # שמירת נתוני המניות

        # משתנים לשמירת התהליכונים
        self.watchlist_worker = None
        self.ai_worker = None

        # פריסה ראשית
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # ניהול מסכים פנימי (דשבורד <-> השקעות)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # יצירת המסכים
        self.dashboard_view = DashboardView()
        self.investment_view = InvestmentView()
        self.trade_controller = TradeController(parent=self, app_controller=self.app)

        self.stack.addWidget(self.dashboard_view)  # אינדקס 0
        self.stack.addWidget(self.investment_view)  # אינדקס 1

        self.setup_connections()

    def setup_connections(self):
        # מעבר מדשבורד ל-"AI Advisor"
        self.dashboard_view.ai_consult_btn.clicked.connect(self.open_advisor_chat)
        # חיבור הכפתור של ה-AI ליצירת המלצה
        self.investment_view.submit_btn.clicked.connect(self.handle_ai_recommendation)
        
        # כפתור חזרה ל-AI Advisor
        self.investment_view.back_btn.clicked.connect(self.back_to_advisor)

        # חיבור כפתור ההתנתקות
        if hasattr(self.dashboard_view, "logout_btn"):
            self.dashboard_view.logout_btn.clicked.connect(self.handle_logout)

        if hasattr(self.dashboard_view, "explorer_btn"):
            self.dashboard_view.explorer_btn.clicked.connect(self.open_explorer)

    def open_advisor_chat(self):
        """מבקש מהאפליקציה הראשית לעבור למסך הצ'אט"""
        print("🔀 Switching to AI Chat Module...")
        if hasattr(self.app, "navigate_to_advisor"):
            self.app.navigate_to_advisor()

    def show_investment(self):
        self.stack.setCurrentWidget(self.investment_view)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_view)
        self.update_user_header()
        self.load_watchlist()

    # --- פונקציות רקע (Background Tasks) ---

    def _ai_task(self, data):
        """שליחת בקשת ההמלצה לשרת ברקע"""
        # אפשר להשתמש ב-requests ישירות או דרך api_client אם תרחיב אותו
        response = requests.post(
            f"http://127.0.0.1:8000/stocks/ai-investment-plan",
            json=data,
            timeout=120,
        )
        if response.status_code == 200:
            return response.json().get("recommendation", "No recommendation available")
        else:
            raise Exception(response.json().get("detail", "Unknown server error"))

    def _watchlist_task(self, user_id):
        """טעינת התיק וחישוב נתונים ברקע (החלק הכבד!)"""
        url = f"http://127.0.0.1:8000/stocks/watchlist/{user_id}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json().get("data", [])
        stocks_processed = []

        for item in data:
            symbol = item.get("symbol")
            avg_buy_price = item.get("price", 0)

            # הבאת מחיר בזמן אמת (זה לוקח זמן ולכן חייב להיות ברקע!)
            current_market_price = self._get_current_price_sync(symbol)
            if current_market_price == 0:
                current_market_price = avg_buy_price

            # חישוב אחוזים
            change_percent = 0
            if avg_buy_price > 0:
                change_percent = ((current_market_price - avg_buy_price) / avg_buy_price) * 100

            stocks_processed.append({
                "event_id": item.get("id"),
                "symbol": symbol,
                "price": current_market_price,
                "buy_price": avg_buy_price,
                "sector": item.get("sector", "Unknown"),
                "change_percent": round(change_percent, 2),
                "amount": item.get("amount", 0),
            })

        return stocks_processed

    def _get_current_price_sync(self, symbol):
        """פונקציית עזר סינכרונית לשימוש בתוך התהליכון"""
        try:
            quote = self.api.get_live_quote(symbol)
            if quote and "price" in quote:
                return quote.get("price")
            return 0
        except:
            return 0

    # --- הנדלרים (UI Handlers) ---

    def handle_ai_recommendation(self):
        """טיפול בלחיצה על הכפתור הירוק (בלי להיתקע!)"""
        # איסוף נתונים
        amount = self.investment_view.amount_input.text()
        if not amount:
            QMessageBox.warning(self.investment_view, "Error", "Please enter investment amount")
            return

        data = {
            "amount": amount,
            "sector": self.investment_view.sector_combo.currentText(),
            "risk": self.investment_view.risk_combo.currentText(),
            "availability": self.investment_view.availability_combo.currentText(),
            "location": self.investment_view.location_combo.currentText(),
        }

        # עדכון UI
        self.investment_view.submit_btn.setEnabled(False)
        self.investment_view.submit_btn.setText("⏳ AI is thinking...")
        self.investment_view.ai_response_box.setText("🔄 Processing your plan... (You can move the window!)")

        # הפעלת Worker
        self.ai_worker = WorkerThread(self._ai_task, data)
        self.ai_worker.finished.connect(self.on_ai_success)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_ai_success(self, recommendation):
        self.investment_view.submit_btn.setEnabled(True)
        self.investment_view.submit_btn.setText("Generate AI Recommendation 🚀")
        self.investment_view.ai_response_box.setText(recommendation)

    def on_ai_error(self, error_msg):
        self.investment_view.submit_btn.setEnabled(True)
        self.investment_view.submit_btn.setText("Generate AI Recommendation 🚀")
        self.investment_view.ai_response_box.setText(f"❌ Error: {error_msg}")
        print(f"[DEBUG] on_ai_error called: {error_msg}")

    def on_buy_error(self, error_msg):
        print(f"[DEBUG] on_buy_error called: {error_msg}")
        QMessageBox.critical(self, "Buy Error", str(error_msg))

    def load_watchlist(self):
        """טעינת התיק ברקע"""
        if not getattr(self.app, "current_user", None): return

        print("📊 Loading Portfolio in background...")
        user_id = self.app.current_user.id

        # אם יש worker קודם שרץ, נסגור אותו קודם
        if hasattr(self, 'watchlist_worker') and self.watchlist_worker is not None:
            if self.watchlist_worker.isRunning():
                print("[DEBUG] load_watchlist: Stopping previous watchlist_worker...")
                self.watchlist_worker.quit()
                self.watchlist_worker.wait()

        # הפעלת Worker לטעינת התיק
        self.watchlist_worker = WorkerThread(self._watchlist_task, user_id)
        self.watchlist_worker.finished.connect(self.display_stocks)  # ברגע שמוכן -> תציג
        self.watchlist_worker.start()

    def display_stocks(self, stocks):
        """הצגת הנתונים בטבלה (רצה ב-Main Thread אחרי שהחישוב הסתיים)"""
        self.dashboard_view.stock_table.setRowCount(len(stocks))
        self.stocks_data = {}

        for row, stock in enumerate(stocks):
            # ... (אותו קוד תצוגה מעולה שלך) ...
            event_id = stock["event_id"]
            symbol = stock["symbol"]
            current_price = stock["price"]
            change_percent = stock["change_percent"]

            # שמירת נתונים למכירה
            self.stocks_data[event_id] = {
                "symbol": symbol,
                "current_price": current_price,
                "amount": stock["amount"],
                "buy_price": stock["buy_price"],
            }

            # צבעים
            if change_percent > 0:
                color = QColor("#a6e3a1")
            elif change_percent < 0:
                color = QColor("#f38ba8")
            else:
                color = QColor("#cdd6f4")

            # מילוי הטבלה
            self.dashboard_view.stock_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.dashboard_view.stock_table.setItem(row, 1, QTableWidgetItem(f"${stock['buy_price']:.2f}"))

            price_item = QTableWidgetItem(f"${current_price:.2f}")
            price_item.setForeground(color)
            self.dashboard_view.stock_table.setItem(row, 2, price_item)

            self.dashboard_view.stock_table.setItem(row, 3, QTableWidgetItem(str(int(stock['amount']))))
            self.dashboard_view.stock_table.setItem(row, 4, QTableWidgetItem(stock['sector']))

            change_text = f"{change_percent:+.2f}%" if change_percent != 0 else "0.00%"
            change_item = QTableWidgetItem(change_text)
            change_item.setForeground(color)
            self.dashboard_view.stock_table.setItem(row, 5, change_item)

            # כפתור מכירה
            sale_btn = QPushButton("📉 Sell")
            sale_btn.setStyleSheet("""
                QPushButton { background-color: #f38ba8; color: #1e1e2e; border-radius: 6px; padding: 5px; border: none; font-weight: bold;}
                QPushButton:hover { background-color: #f5b9d6; }
            """)
            sale_btn.setCursor(Qt.PointingHandCursor)
            sale_btn.clicked.connect(lambda ch, eid=event_id: self.open_sale_dialog(eid))
            self.dashboard_view.stock_table.setCellWidget(row, 6, sale_btn)

    def handle_logout(self):
        if hasattr(self.app, "logout"):
            self.app.logout()

    def open_explorer(self):
        if hasattr(self.app, "navigate_to_explorer"):
            self.app.navigate_to_explorer()

    def update_user_header(self):
        try:
            if getattr(self.app, "current_user", None):
                name = self.app.current_user.full_name or self.app.current_user.email
                self.dashboard_view.user_label.setText(f"Welcome, {name}")
        except:
            pass

    def open_sale_dialog(self, event_id):
        if event_id in self.stocks_data:
            s = self.stocks_data[event_id]
            self.trade_controller.open_sale_window(s["symbol"], s["current_price"], s["amount"], s["buy_price"],
                                                   event_id)

    # פונקציות להוספה עתידית (Search Dialog)
    def handle_add_stock(self):
        pass

    def add_stock_entry(self, stock):
        self.load_watchlist()
    
    def back_to_advisor(self):
        """חזרה למסך היועץ לאחר סיום/ביטול טופס ההשקעה"""
        if hasattr(self.app, "navigate_to_advisor"):
            self.app.navigate_to_advisor()