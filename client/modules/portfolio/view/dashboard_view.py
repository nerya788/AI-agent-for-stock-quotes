from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHeaderView)
from PySide6.QtCore import Qt

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout() # חלוקה לצדדים (תפריט צד ותוכן מרכזי)
        
        # --- תפריט צד ---
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 20, 10, 20)
        
        self.user_label = QLabel("Welcome, User!")
        self.user_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        sidebar.addWidget(self.user_label)

        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; margin-top: 20px;")
        sidebar.addWidget(self.logout_btn)
        
        self.ai_consult_btn = QPushButton("🤖 AI Advisor")
        self.ai_consult_btn.setStyleSheet("background-color: #f5c2e7; color: #11111b;")
        sidebar.addWidget(self.ai_consult_btn)
        
        self.explorer_btn = QPushButton("📈 Market Explorer")
        self.explorer_btn.setStyleSheet("background-color: #89dceb; color: #11111b; margin-top: 10px;")
        sidebar.addWidget(self.explorer_btn)

        sidebar.addStretch() # דוחף הכל למעלה
        
        layout.addLayout(sidebar, 1)

        # --- תוכן מרכזי ---
        main_content = QVBoxLayout()
        
        stats_label = QLabel("My Portfolio Overview")
        stats_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_content.addWidget(stats_label)

        # טבלת מניות
        self.stock_table = QTableWidget(0, 4)
        self.stock_table.setHorizontalHeaderLabels(["Symbol", "Price", "Sector", "Change %"])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setStyleSheet("background-color: #313244; gridline-color: #45475a;")
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_content.addWidget(self.stock_table)

        layout.addLayout(main_content, 3)
        self.setLayout(layout)