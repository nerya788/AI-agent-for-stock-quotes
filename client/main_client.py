import sys
import os

# הוספת תיקיית השורש של הפרויקט לנתיב כדי שיוכל למצוא את ה-views וה-api_client
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PySide6.QtWidgets import QApplication, QStackedWidget, QMainWindow, QMessageBox
from views.login_view import LoginView
from views.register_view import RegisterView
from views.dashboard_view import DashboardView
from views.investment_view import InvestmentView
from api_client import APIClient

GLOBAL_STYLE = """
    QMainWindow, QStackedWidget, QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Segoe UI', sans-serif;
    }
    QLineEdit {
        background-color: #313244;
        border: 1px solid #45475a;
        border-radius: 10px;
        padding: 12px;
        color: white;
    }
    QLineEdit:focus {
        border: 1px solid #89b4fa;
    }
    QPushButton {
        background-color: #89b4fa;
        color: #11111b;
        border-radius: 10px;
        padding: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #b4befe;
    }
    QComboBox {
        background-color: #313244;
        border: 1px solid #45475a;
        border-radius: 8px;
        padding: 8px;
        color: white;
    }
"""

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockQuotes AI Portal")
        self.setFixedSize(1000, 750)

        self.api = APIClient()
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # יצירת הדפים
        self.login_page = LoginView()
        self.register_page = RegisterView()
        self.dashboard_page = DashboardView()
        self.investment_page = InvestmentView()

        # הוספה ל-Stack
        self.stack.addWidget(self.login_page)      # 0
        self.stack.addWidget(self.register_page)   # 1
        self.stack.addWidget(self.dashboard_page)  # 2
        self.stack.addWidget(self.investment_page) # 3

        # חיבור הלוגיקה והמעברים
        self.setup_connections()

    def setup_connections(self):
        # מעברים
        self.login_page.switch_to_register.connect(lambda: self.stack.setCurrentIndex(1))
        self.register_page.switch_to_login.connect(lambda: self.stack.setCurrentIndex(0))
        self.dashboard_page.ai_consult_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        # חיבור כפתורי פעולה לפונקציות (חובה שיהיו בתוך ה-Class!)
        self.login_page.login_btn.clicked.connect(self.handle_login)
        self.register_page.reg_btn.clicked.connect(self.handle_register)

    def handle_login(self):
        """לוגיקה של כניסה למערכת"""
        email = self.login_page.email_input.text()
        password = self.login_page.pass_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        print(f"📡 Presenter: Authenticating {email}...")
        # מעבר אוטומטי לדשבורד לצורך בדיקה
        self.dashboard_page.user_label.setText(f"Welcome, {email.split('@')[0]}!")
        self.stack.setCurrentIndex(2)

    def handle_register(self):
        """לוגיקה של רישום משתמש חדש"""
        name = self.register_page.name_input.text()
        email = self.register_page.email_input.text()
        password = self.register_page.pass_input.text()
        
        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        try:
            print(f"📡 Presenter: Registering {email}...")
            response = self.api.register(email, password, name)
            
            if response.get("status") == "success":
                QMessageBox.information(self, "Success", "Account created successfully!")
                self.stack.setCurrentIndex(0)
            else:
                QMessageBox.critical(self, "Error", response.get("detail", "Failed to register"))
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not reach server: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    
    controller = MainController()
    controller.show()
    sys.exit(app.exec())