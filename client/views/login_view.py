from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

class LoginView(QWidget):
    # סיגנל שמודיע למנהל המערכת לעבור לדף רישום
    switch_to_register = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("StockQuotes AI")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #89b4fa; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Sign in to manage your portfolio")
        subtitle.setStyleSheet("font-size: 14px; color: #a6adc8; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        layout.addWidget(self.email_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        self.login_btn = QPushButton("Sign In")
        layout.addWidget(self.login_btn)

        # כפתור מעבר לרישום
        self.go_to_reg_btn = QPushButton("New here? Create an account")
        self.go_to_reg_btn.setStyleSheet("background: transparent; color: #f5e0dc; text-decoration: underline;")
        self.go_to_reg_btn.setCursor(Qt.PointingHandCursor)
        self.go_to_reg_btn.clicked.connect(self.switch_to_register.emit)
        layout.addWidget(self.go_to_reg_btn)

        self.setLayout(layout)