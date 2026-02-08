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

# וודא שהקבצים האלו אכן נמצאים בתיקיית views של המודול
from client.modules.portfolio.view.dashboard_view import DashboardView
from client.modules.portfolio.view.investment_view import InvestmentView
from client.modules.trade.controller.trade_controller import TradeController
from client.core.api_client import APIClient

# from client.modules.portfolio.view.stock_search_dialog import StockSearchDialog
# TODO: Uncomment once stock_search_dialog.py is created in the view folder


class PortfolioController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.api = APIClient()
        self.stocks_data = {}  # שמירת נתוני המניות

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
        self.trade_controller = TradeController(parent=None, app_controller=self.app)

        self.stack.addWidget(self.dashboard_view)  # אינדקס 0
        self.stack.addWidget(self.investment_view)  # אינדקס 1

        self.setup_connections()

    def setup_connections(self):
        # מעבר מדשבורד ל-"AI Advisor"
        self.dashboard_view.ai_consult_btn.clicked.connect(self.show_investment)

        # חיבור הכפתור של ה-AI ליצירת המלצה
        self.investment_view.submit_btn.clicked.connect(self.handle_ai_recommendation)

        # כפתור חזרה לדשבורד
        self.investment_view.back_btn.clicked.connect(self.show_dashboard)

        # חיבור כפתור ההתנתקות (Logout) - וודא שהוא קיים ב-DashboardView
        if hasattr(self.dashboard_view, "logout_btn"):
            self.dashboard_view.logout_btn.clicked.connect(self.handle_logout)

        if hasattr(self.dashboard_view, "explorer_btn"):
            self.dashboard_view.explorer_btn.clicked.connect(self.open_explorer)

    def show_investment(self):
        self.stack.setCurrentWidget(self.investment_view)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_view)
        self.update_user_header()
        self.load_watchlist()

    def handle_ai_recommendation(self):
        """
        שליחה של טופס ההשקעה ל-AI לקבלת המלצה
        """
        # קבלת הנתונים מהטופס
        amount = self.investment_view.amount_input.text()
        sector = self.investment_view.sector_combo.currentText()
        risk = self.investment_view.risk_combo.currentText()
        availability = self.investment_view.availability_combo.currentText()
        location = self.investment_view.location_combo.currentText()

        # ולידציה
        if not amount:
            QMessageBox.warning(self.investment_view, "שגיאה", "נא להכניס סכום השקעה")
            return

        # הודעה בממשק שמעבדים + השבתת כפתור
        self.investment_view.submit_btn.setEnabled(False)
        self.investment_view.submit_btn.setText("⏳ Loading...")
        self.investment_view.ai_response_box.setText(
            "🔄 Processing your investment plan with AI..."
        )

        try:
            # שימוש ב-API Client במקום requests ישיר (יותר נכון ארכיטקטונית)
            data = {
                "amount": amount,
                "sector": sector,
                "risk": risk,
                "availability": availability,
                "location": location,
            }

            # אם כבר הוספת את הפונקציה ב-APIClient תשתמש בה, אם לא - נשתמש ב-requests ישירות לבינתיים
            # response = self.api.get_investment_plan(data)

            response = requests.post(
                f"http://127.0.0.1:8000/stocks/ai-investment-plan",
                json=data,
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()
                recommendation = result.get(
                    "recommendation", "No recommendation available"
                )
                self.investment_view.ai_response_box.setText(recommendation)
            else:
                error_msg = response.json().get("detail", "Unknown error")
                self.investment_view.ai_response_box.setText(f"❌ Error: {error_msg}")

        except Exception as e:
            error_msg = f"❌ Connection Error: {str(e)}"
            self.investment_view.ai_response_box.setText(error_msg)
        finally:
            # החזרת הכפתור לנורמל
            self.investment_view.submit_btn.setEnabled(True)
            self.investment_view.submit_btn.setText("Generate AI Recommendation 🚀")

    # --- הנה הפונקציה החסרה (חייבת להיות באותו קו הזחה כמו def handle_ai_recommendation) ---
    def handle_logout(self):
        """מטפל בלחיצה על כפתור ההתנתקות"""
        print("👋 Portfolio: Logging out...")
        # קריאה לפונקציה הראשית ב-AppController
        if hasattr(self.app, "logout"):
            self.app.logout()
        else:
            print("❌ Error: AppController does not have a logout method!")

    def open_explorer(self):
        """מעבר למודול ה-Explorer דרך האפליקציה הראשית"""
        print("🚀 Navigating to Market Explorer...")
        if hasattr(self.app, "navigate_to_explorer"):
            self.app.navigate_to_explorer()
        else:
            print("❌ Error: AppController missing navigate_to_explorer method")

    def update_user_header(self):
        """עדכון טקסט המשתמש בדשבורד"""
        try:
            if getattr(self.app, "current_user", None):
                name = self.app.current_user.full_name or self.app.current_user.email
                self.dashboard_view.user_label.setText(f"Welcome, {name}")
        except Exception:
            pass

    def load_watchlist(self):
        """טעינת התיק וחישוב רווח/הפסד בזמן אמת"""
        print("📊 Loading Smart Portfolio...")

        if not getattr(self.app, "current_user", None):
            return
        user_id = self.app.current_user.id

        try:
            # שליפה מהתיק (שעכשיו מכיל ממוצעים מחושבים)
            url = f"http://127.0.0.1:8000/stocks/watchlist/{user_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json().get("data", [])
                stocks = []

                for item in data:
                    symbol = item.get("symbol")
                    amount = item.get("amount", 0)
                    sector = item.get("sector", "Unknown")

                    # זה המחיר הממוצע המשוקלל שחישבנו בשרת!
                    avg_buy_price = item.get("price", 0)

                    # משיכת מחיר שוק נוכחי (בזמן אמת)
                    # (חשוב: הפונקציה get_current_price צריכה לעבוד מול API אמיתי או Mock)
                    current_market_price = self.get_current_price(symbol)

                    # אם ה-API נכשל והחזיר 0, נשתמש במחיר הקנייה כברירת מחדל לתצוגה
                    if current_market_price == 0:
                        current_market_price = avg_buy_price

                    # חישוב אחוז השינוי: (מחיר עכשיו - מחיר ממוצע) / מחיר ממוצע
                    change_percent = 0
                    if avg_buy_price > 0:
                        change_percent = (
                            (current_market_price - avg_buy_price) / avg_buy_price
                        ) * 100

                    stock_display = {
                        "event_id": item.get("id"),
                        "symbol": symbol,
                        "price": current_market_price,  # מוצג בטור "Current Price"
                        "buy_price": avg_buy_price,  # מוצג בטור "Avg Buy Price"
                        "sector": sector,
                        "change_percent": round(change_percent, 2),  # השינוי האמיתי!
                        "amount": amount,
                    }
                    stocks.append(stock_display)

                self.display_stocks(stocks)
            else:
                self.display_stocks([])

        except Exception as e:
            print(f"❌ Error loading portfolio: {e}")
            self.display_stocks([])

    def get_current_price(self, symbol):
        """קבלת המחיר הנוכחי של מניה"""
        try:
            quote = self.api.get_live_quote(symbol)
            if quote and "price" in quote:
                return quote.get("price")
            return 0
        except Exception as e:
            print(f"⚠️ Error getting current price for {symbol}: {e}")
            return 0

    def display_stocks(self, stocks):
        """הצגת מניות בטבלה - כל קנייה בשורה נפרדת"""
        self.dashboard_view.stock_table.setRowCount(len(stocks))

        # שמור את נתוני המניות לשימוש כשלוחצים על Sale
        self.stocks_data = {}

        for row, stock in enumerate(stocks):
            event_id = stock.get("event_id")  # ID ייחודי לקנייה
            symbol = str(stock.get("symbol", ""))
            current_price = stock.get("price", 0)  # המחיר הנוכחי
            amount = stock.get("amount", 0)  # כמות הקנייה הספציפית
            change_percent = stock.get("change_percent", 0)
            buy_price = stock.get("buy_price", 0)  # מחיר קנייה

            # שמור את נתוני המניה לפי event_id
            self.stocks_data[event_id] = {
                "symbol": symbol,
                "current_price": current_price,
                "amount": amount,
                "buy_price": buy_price,
            }

            # צביעת השורה לפי שינוי - ירוק (חיובי), אדום (שלילי), לבן (אפס)
            if change_percent > 0:
                color = QColor("#a6e3a1")  # ירוק
            elif change_percent < 0:
                color = QColor("#f38ba8")  # אדום
            else:
                color = QColor("#cdd6f4")  # לבן

            # עמודה 0: Symbol
            self.dashboard_view.stock_table.setItem(row, 0, QTableWidgetItem(symbol))

            # עמודה 1: מחיר קנייה
            buy_price_item = QTableWidgetItem(f"${buy_price:.2f}")
            self.dashboard_view.stock_table.setItem(row, 1, buy_price_item)

            # עמודה 2: המחיר הנוכחי
            price_item = QTableWidgetItem(f"${current_price:.2f}")
            price_item.setForeground(color)
            self.dashboard_view.stock_table.setItem(row, 2, price_item)

            # עמודה 3: כמות הקנייה
            qty_item = QTableWidgetItem(str(int(amount)))
            self.dashboard_view.stock_table.setItem(row, 3, qty_item)

            # עמודה 4: Sector
            self.dashboard_view.stock_table.setItem(
                row, 4, QTableWidgetItem(str(stock.get("sector", "N/A")))
            )

            # עמודה 5: השינוי באחוזים עם צביעה
            if change_percent == 0:
                change_text = f"{change_percent:.2f}%"
            else:
                change_text = f"{change_percent:+.2f}%"
            change_item = QTableWidgetItem(change_text)
            change_item.setForeground(color)
            self.dashboard_view.stock_table.setItem(row, 5, change_item)

            # עמודה 6: כפתור Sale
            sale_btn = QPushButton("📉 Sell")
            sale_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #f38ba8;
                    color: #1e1e2e;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 8px 12px;
                    border: none;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #f5b9d6;
                }
                QPushButton:pressed {
                    background-color: #e8738d;
                }
            """
            )
            sale_btn.setCursor(Qt.PointingHandCursor)
            sale_btn.clicked.connect(
                lambda checked, eid=event_id: self.open_sale_dialog(eid)
            )
            self.dashboard_view.stock_table.setCellWidget(row, 6, sale_btn)

    def handle_add_stock(self):
        """פתיחת דיאלוג חיפוש מניות והוספה"""
        if not getattr(self.app, "current_user", None):
            QMessageBox.warning(self, "שגיאה", "אין משתמש מחובר")
            return

        user_id = getattr(self.app.current_user, "id", None)
        if not user_id:
            QMessageBox.warning(self, "שגיאה", "לא נמצא מזהה משתמש")
            return

        dialog = StockSearchDialog(self)
        if dialog.exec() and dialog.selected_stock:
            self.add_stock_entry(dialog.selected_stock)

    def add_stock_entry(self, stock):
        """
        רענון התצוגה אחרי קנייה.
        אין צורך לשמור שוב - השרת כבר שמר! אנחנו רק מושכים את המידע העדכני.
        """
        print(
            f"🔄 Trade completed for {stock.get('symbol')}. Refreshing watchlist from server..."
        )

        # פשוט קוראים לפונקציה שכבר כתבת מצוין, שטוענת הכל מחדש מהשרת
        self.load_watchlist()

    def open_sale_dialog(self, event_id):
        """פתיחת דיאלוג מכירה לקנייה ספציפית"""
        if event_id not in self.stocks_data:
            QMessageBox.warning(self.dashboard_view, "Error", "Stock data not found")
            return

        stock_info = self.stocks_data[event_id]
        symbol = stock_info["symbol"]
        current_price = stock_info["current_price"]
        amount = stock_info["amount"]
        buy_price = stock_info["buy_price"]

        print(
            f"📉 Opening sale dialog for {symbol} (event {event_id}): price=${current_price}, qty={amount}"
        )

        self.trade_controller.open_sale_window(
            symbol, current_price, amount, buy_price, event_id
        )
