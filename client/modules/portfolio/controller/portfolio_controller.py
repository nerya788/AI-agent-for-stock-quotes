from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox, QTableWidgetItem
import requests
# וודא שהקבצים האלו אכן נמצאים בתיקיית views של המודול
from client.modules.portfolio.view.dashboard_view import DashboardView
from client.modules.portfolio.view.investment_view import InvestmentView
from client.core.api_client import APIClient

# from client.modules.portfolio.view.stock_search_dialog import StockSearchDialog
# TODO: Uncomment once stock_search_dialog.py is created in the view folder

class PortfolioController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.api = APIClient()
        
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
        
        self.stack.addWidget(self.dashboard_view)   # אינדקס 0
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
        if hasattr(self.dashboard_view, 'logout_btn'):
            self.dashboard_view.logout_btn.clicked.connect(self.handle_logout)
        
        if hasattr(self.dashboard_view, 'explorer_btn'):
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
        self.investment_view.ai_response_box.setText("🔄 Processing your investment plan with AI...")
        
        try:
            # שימוש ב-API Client במקום requests ישיר (יותר נכון ארכיטקטונית)
            data = {
                "amount": amount,
                "sector": sector,
                "risk": risk,
                "availability": availability,
                "location": location
            }
            
            # אם כבר הוספת את הפונקציה ב-APIClient תשתמש בה, אם לא - נשתמש ב-requests ישירות לבינתיים
            # response = self.api.get_investment_plan(data)
            
            response = requests.post(f"http://127.0.0.1:8000/stocks/ai-investment-plan", json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                recommendation = result.get("recommendation", "No recommendation available")
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
        if hasattr(self.app, 'logout'):
            self.app.logout()
        else:
            print("❌ Error: AppController does not have a logout method!")
        
    def open_explorer(self):
        """מעבר למודול ה-Explorer דרך האפליקציה הראשית"""
        print("🚀 Navigating to Market Explorer...")
        if hasattr(self.app, 'navigate_to_explorer'):
            self.app.navigate_to_explorer()
        else:
            print("❌ Error: AppController missing navigate_to_explorer method")

    def update_user_header(self):
        """עדכון טקסט המשתמש בדשבורד"""
        try:
            if getattr(self.app, 'current_user', None):
                name = self.app.current_user.full_name or self.app.current_user.email
                self.dashboard_view.user_label.setText(f"Welcome, {name}")
        except Exception:
            pass

    def load_watchlist(self):
        """טעינת רשימת המעקב של המשתמש מSupabase"""
        if not getattr(self.app, 'current_user', None):
            self.display_stocks([])
            return

        user_id = getattr(self.app.current_user, 'id', None)
        if not user_id:
            self.display_stocks([])
            return

        try:
            # טעינת קניות מ-stock_events עם user_id
            response = requests.get(f"http://127.0.0.1:8000/stocks/user-purchases/{user_id}", timeout=5)
            
            if response.status_code == 200:
                events = response.json().get("data", [])
                
                # המרת stock_events לפורמט של display_stocks
                stocks = []
                for event in events:
                    if event.get("event_type") == "STOCK_PURCHASED":
                        payload = event.get("payload", {})
                        stock = {
                            "symbol": event.get("symbol"),
                            "price": payload.get("price", 0),
                            "sector": "N/A",
                            "change_percent": 0,
                            "amount": payload.get("amount", 0)
                        }
                        stocks.append(stock)
                
                self.display_stocks(stocks)
            else:
                self.display_stocks([])
        except Exception as e:
            print(f"❌ Error loading purchases: {e}")
            self.display_stocks([])

    def display_stocks(self, stocks):
        """הצגת מניות בטבלה"""
        self.dashboard_view.stock_table.setRowCount(len(stocks))

        for row, stock in enumerate(stocks):
            self.dashboard_view.stock_table.setItem(row, 0, QTableWidgetItem(str(stock.get("symbol", ""))))
            self.dashboard_view.stock_table.setItem(row, 1, QTableWidgetItem(f"${stock.get('price', 0)}"))
            self.dashboard_view.stock_table.setItem(row, 2, QTableWidgetItem(str(stock.get("sector", "N/A"))))
            self.dashboard_view.stock_table.setItem(row, 3, QTableWidgetItem(str(stock.get("change_percent", 0))))

    def handle_add_stock(self):
        """פתיחת דיאלוג חיפוש מניות והוספה"""
        if not getattr(self.app, 'current_user', None):
            QMessageBox.warning(self, "שגיאה", "אין משתמש מחובר")
            return

        user_id = getattr(self.app.current_user, 'id', None)
        if not user_id:
            QMessageBox.warning(self, "שגיאה", "לא נמצא מזהה משתמש")
            return

        dialog = StockSearchDialog(self)
        if dialog.exec() and dialog.selected_stock:
            self.add_stock_entry(dialog.selected_stock)

    def add_stock_entry(self, stock):
        """הוסף מניה לSupabase לפי משתמש"""
        if not getattr(self.app, 'current_user', None):
            return

        symbol = (stock.get("symbol") or "").upper()
        if not symbol:
            return

        user_id = getattr(self.app.current_user, 'id', None)
        if not user_id:
            return

        price = stock.get("price")
        if price is None:
            quote = self.api.get_live_quote(symbol)
            if quote and "price" in quote:
                price = quote.get("price")

        try:
            entry = {
                "user_id": user_id,
                "symbol": symbol,
                "price": price if price is not None else 0,
                "sector": stock.get("sector", "N/A"),
                "change_percent": stock.get("change_percent", 0),
                "amount": stock.get("amount", 1)
            }

            from server.repositories.stock_repository import StockRepository
            repo = StockRepository()
            repo.supabase.table("stocks_watchlist").insert(entry).execute()
            print(f"✅ {symbol} saved to Supabase for user {user_id}")
            
            self.load_watchlist()
        except Exception as e:
            print(f"❌ Error saving stock: {e}")