from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QListWidget, QListWidgetItem, QLabel)
from PySide6.QtCore import Qt, Signal

class AdvisorView(QWidget):
    # זה הסיגנל שהיה חסר לקונטרולר!
    send_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # כותרת
        top_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setStyleSheet("background-color: #45475a; color: white; padding: 8px 15px; border-radius: 5px; font-weight: bold;")
        self.back_btn.setCursor(Qt.PointingHandCursor)

        header = QLabel("AI Financial Advisor 🤖")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #cba6f7;")
        header.setAlignment(Qt.AlignCenter)

        top_layout.addWidget(self.back_btn)
        top_layout.addWidget(header, 1)

        layout.addLayout(top_layout)
        
        # אזור ההיסטוריה של הצ'אט (במקום סתם תיבת טקסט)
        self.chat_history = QListWidget()
        self.chat_history.setStyleSheet("""
            QListWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                color: #cdd6f4;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        self.chat_history.setWordWrap(True)
        # גלילה חלקה
        self.chat_history.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        layout.addWidget(self.chat_history)

        # אזור ההקלדה (Input Area)
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything about stocks, or say 'buy AAPL'...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                background: #45475a; 
                color: white; 
                border-radius: 5px;
                border: 1px solid #585b70;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
        """)
        self.input_field.returnPressed.connect(self.handle_send) # שליחה ב-Enter
        
        self.send_btn = QPushButton("Send 🚀")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7; 
                color: #1e1e2e; 
                padding: 10px 20px; 
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d8c3f5;
            }
        """)
        self.send_btn.clicked.connect(self.handle_send)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        self.setLayout(layout)

    def handle_send(self):
        text = self.input_field.text().strip()
        if text:
            # הוספת ההודעה של המשתמש לצ'אט מיד
            self.add_message("You", text, Qt.AlignRight)
            # שידור הסיגנל לקונטרולר
            self.send_message.emit(text)
            self.input_field.clear()

    def add_message(self, sender, text, alignment):
        """פונקציית עזר להוספת הודעות יפות לצ'אט"""
        item = QListWidgetItem(f"{sender}: {text}")
        item.setTextAlignment(alignment)
        
        # צבע שונה ל-AI ולמשתמש
        if sender == "AI":
            item.setForeground(Qt.cyan) # או כל צבע שתרצה
        else:
            item.setForeground(Qt.white)
            
        self.chat_history.addItem(item)
        self.chat_history.scrollToBottom()