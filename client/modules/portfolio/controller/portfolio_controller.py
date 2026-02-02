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
        
        print(f"📊 PortfolioController: Generating AI recommendation...")
        print(f"   Amount: ${amount}")
        print(f"   Sector: {sector}")
        print(f"   Risk: {risk}")
        print(f"   Availability: {availability}")
        print(f"   Location: {location}")
        
        # הודעה בממשק שמעבדים + השבתת כפתור
        self.investment_view.submit_btn.setEnabled(False)
        self.investment_view.submit_btn.setText("⏳ Loading...")
        self.investment_view.ai_response_box.setText("🔄 Processing your investment plan with AI...\nThis may take a few seconds. Please wait...")
        
        try:
            # בניית בקשה לשרת
            prompt = f"""
            Create an investment plan for a client with:
            - Investment Amount: ${amount}
            - Preferred Sector: {sector}
            - Risk Tolerance: {risk}
            - Investment Availability: {availability}
            - Market Focus: {location}
            
            Provide specific stock recommendations, allocation percentages, and risk assessment.
            """
            
            # שליחה לשרת (ל-AI analyze endpoint)
            response = requests.post(f"http://127.0.0.1:8000/stocks/ai-investment-plan", json={
                "amount": amount,
                "sector": sector,
                "risk": risk,
                "availability": availability,
                "location": location
            }, timeout=120)  # הגדלת timeout ל-2 דקות
            
            if response.status_code == 200:
                result = response.json()
                recommendation = result.get("recommendation", "No recommendation available")
                
                # הצגת התוצאה בתיבה
                self.investment_view.ai_response_box.setText(recommendation)
                print(f"✅ AI Recommendation generated successfully")
            else:
                error_msg = response.json().get("detail", "Unknown error")
                self.investment_view.ai_response_box.setText(f"❌ Error: {error_msg}")
                print(f"❌ AI Error: {error_msg}")
                
        except requests.exceptions.Timeout:
            error_msg = "⏱️ AI analysis in progress... This may take up to 2 minutes for Llama3. Please wait."
            self.investment_view.ai_response_box.setText(error_msg)
            print(f"⏱️ Timeout (Llama3 processing...)")
        except Exception as e:
            error_msg = f"❌ Connection Error: {str(e)}"
            self.investment_view.ai_response_box.setText(error_msg)
            print(f"❌ {error_msg}")
        finally:
            # החזרת הכפתור לנורמל
            self.investment_view.submit_btn.setEnabled(True)
            self.investment_view.submit_btn.setText("Generate AI Recommendation 🚀")