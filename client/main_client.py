import sys
import os

# תיקון נתיבים
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from client.modules.auth.controller.auth_controller import AuthController
# --- הוספנו את הייבוא של הפורטפוליו ---
from client.modules.portfolio.controller.portfolio_controller import PortfolioController

GLOBAL_STYLE = """
    /* הגדרות צבעים כלליות (בלי גודל פונט כאן!) */
    QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Segoe UI', sans-serif;
    }

    /* הגדרת גודל פונט רק לרכיבים רלוונטיים */
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget, QHeaderView {
        font-size: 14px;
    }

    /* תיקון לשדות קלט */
    QLineEdit {
        background-color: #313244;
        color: #ffffff;
        border: 1px solid #45475a;
        border-radius: 8px;
        padding: 8px;
    }
    QLineEdit:focus {
        border: 1px solid #89b4fa;
    }

    /* עיצוב כפתורים */
    QPushButton {
        background-color: #89b4fa;
        color: #1e1e2e;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #b4befe;
    }

    /* כותרות ותוויות */
    QLabel {
        color: #cdd6f4;
    }

    /* עיצוב לטבלאות (דשבורד) */
    QTableWidget {
        background-color: #313244;
        gridline-color: #45475a;
        color: white;
        border: none; /* הורדת מסגרת לטבלה נקייה יותר */
    }
    QHeaderView::section {
        background-color: #1e1e2e;
        color: #cdd6f4;
        padding: 6px;
        border: 1px solid #45475a;
        font-weight: bold;
    }
"""

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockQuotes Enterprise System")
        self.setFixedSize(1200, 800) # הגדלתי קצת שיהיה נוח

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 1. אתחול Auth
        self.auth_module = AuthController(self)
        self.stack.addWidget(self.auth_module)

        # 2. אתחול Portfolio (עכשיו זה פעיל!)
        self.portfolio_module = PortfolioController(self)
        self.stack.addWidget(self.portfolio_module)
        
        # מתחילים במסך כניסה
        self.stack.setCurrentWidget(self.auth_module)

    def navigate_to_portfolio(self):
        print("Navigation: Moving to Portfolio Module")
        # --- השורה הזאת עושה את הקסם ---
        self.stack.setCurrentWidget(self.portfolio_module)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    
    window = MainApp()
    window.show()
    sys.exit(app.exec())