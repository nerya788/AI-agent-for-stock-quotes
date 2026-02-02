from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QMessageBox
import requests
# וודא שהקבצים האלו אכן נמצאים בתיקיית views של המודול
from client.modules.portfolio.view.dashboard_view import DashboardView
from client.modules.portfolio.view.investment_view import InvestmentView
from client.core.api_client import APIClient

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