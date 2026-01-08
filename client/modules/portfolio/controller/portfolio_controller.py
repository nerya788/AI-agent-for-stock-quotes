from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
# וודא שהקבצים האלו אכן נמצאים בתיקיית views של המודול
from client.modules.portfolio.view.dashboard_view import DashboardView
from client.modules.portfolio.view.investment_view import InvestmentView

class PortfolioController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        
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
        
        # (אופציונלי) כפתור חזרה מהשאלון לדשבורד - נצטרך להוסיף כפתור כזה ב-View אם תרצה
        # self.investment_view.back_btn.clicked.connect(self.show_dashboard)

    def show_investment(self):
        self.stack.setCurrentWidget(self.investment_view)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_view)