import sys
import os
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from client.modules.auth.controller.auth_controller import AuthController
from client.modules.portfolio.controller.portfolio_controller import PortfolioController

# הגדרת העיצוב (שמנו אותה כאן כדי שתהיה זמינה לקונטרולר)
GLOBAL_STYLE = """
    QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Segoe UI', sans-serif;
    }
    QLabel, QPushButton, QLineEdit, QTextEdit, QTableWidget, QHeaderView {
        font-size: 14px;
    }
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
    QLabel {
        color: #cdd6f4;
    }
    QTableWidget {
        background-color: #313244;
        gridline-color: #45475a;
        color: white;
        border: none;
    }
    QHeaderView::section {
        background-color: #1e1e2e;
        color: #cdd6f4;
        padding: 6px;
        border: 1px solid #45475a;
        font-weight: bold;
    }
"""

class AppController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockQuotes Enterprise System")
        self.setFixedSize(1200, 800)
        
        self.current_user = None 

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # אתחול המודולים
        self.auth_module = AuthController(self)
        self.portfolio_module = PortfolioController(self)

        self.stack.addWidget(self.auth_module)     # Index 0
        self.stack.addWidget(self.portfolio_module) # Index 1
        
        self.stack.setCurrentWidget(self.auth_module)

    def set_user_session(self, user_model):
        """שמירת פרטי המשתמש המחובר"""
        self.current_user = user_model
        self.setWindowTitle(f"StockQuotes Enterprise - {user_model.full_name}")
        print(f"🔑 Session Started for: {user_model.full_name}")

    def navigate_to_portfolio(self):
        print("Navigation: Moving to Portfolio Module")
        self.stack.setCurrentWidget(self.portfolio_module)