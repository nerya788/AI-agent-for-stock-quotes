from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit)
from PySide6.QtCore import Qt

class AdvisorView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # כותרת
        header = QLabel("AI Financial Advisor 🤖")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #cba6f7;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # אזור שאלה / חיפוש
        input_layout = QHBoxLayout()
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter stock symbol to analyze (e.g. AAPL)...")
        self.symbol_input.setStyleSheet("padding: 10px; background: #313244; color: white; border-radius: 5px;")
        
        self.analyze_btn = QPushButton("Ask AI")
        self.analyze_btn.setStyleSheet("background-color: #cba6f7; color: #1e1e2e; padding: 10px; font-weight: bold;")
        
        input_layout.addWidget(self.symbol_input)
        input_layout.addWidget(self.analyze_btn)
        layout.addLayout(input_layout)

        # אזור תשובה
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setPlaceholderText("AI insights will appear here...")
        self.result_area.setStyleSheet("""
            QTextEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.result_area)

        self.setLayout(layout)