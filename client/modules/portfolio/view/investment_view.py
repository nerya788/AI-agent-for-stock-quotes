from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QComboBox, QTextEdit, QFrame)
from PySide6.QtCore import Qt

class InvestmentView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # פריסה ראשית - שני טורים (טופס ותשובה)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- טור שמאל: הטופס ---
        form_layout = QVBoxLayout()
        
        header = QLabel("Personalized Investment Plan")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #89b4fa;")
        form_layout.addWidget(header)

        # שדות השאלון
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Investment Amount (e.g. 50,000)")
        form_layout.addWidget(QLabel("How much would you like to invest?"))
        form_layout.addWidget(self.amount_input)

        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["Technology", "Energy", "Agriculture", "Real Estate", "Healthcare"])
        form_layout.addWidget(QLabel("Preferred Sector:"))
        form_layout.addWidget(self.sector_combo)

        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["Low (Conservative)", "Medium (Balanced)", "High (Aggressive)"])
        form_layout.addWidget(QLabel("Risk Tolerance:"))
        form_layout.addWidget(self.risk_combo)

        self.availability_combo = QComboBox()
        self.availability_combo.addItems(["Short Term (< 1 year)", "Medium Term (1-5 years)", "Long Term (5+ years)"])
        form_layout.addWidget(QLabel("Investment Availability:"))
        form_layout.addWidget(self.availability_combo)

        self.location_combo = QComboBox()
        self.location_combo.addItems(["Israel", "Abroad (Global)", "Combined"])
        form_layout.addWidget(QLabel("Market Focus:"))
        form_layout.addWidget(self.location_combo)

        self.submit_btn = QPushButton("Generate AI Recommendation 🚀")
        self.submit_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; padding: 15px; font-size: 16px;")
        form_layout.addWidget(self.submit_btn)
        
        form_layout.addStretch()
        main_layout.addLayout(form_layout, 1)

        # --- טור ימין: חלונית תשובת הסוכן ---
        result_container = QVBoxLayout()
        
        result_label = QLabel("AI Agent Analysis")
        result_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f5c2e7;")
        result_container.addWidget(result_label)

        # מסגרת מעוצבת לתשובה
        self.ai_response_box = QTextEdit()
        self.ai_response_box.setReadOnly(True)
        self.ai_response_box.setPlaceholderText("Fill the form and click generate to see AI insights...")
        self.ai_response_box.setStyleSheet("""
            QTextEdit {
                background-color: #313244;
                border: 2px solid #f5c2e7;
                border-radius: 15px;
                padding: 20px;
                color: #cdd6f4;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        result_container.addWidget(self.ai_response_box)
        
        main_layout.addLayout(result_container, 1)
        self.setLayout(main_layout)