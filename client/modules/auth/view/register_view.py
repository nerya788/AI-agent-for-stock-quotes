from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

class RegisterView(QWidget):
    # סיגנל לחזרה לכניסה
    switch_to_login = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Create Account")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #a6e3a1; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        layout.addWidget(self.email_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        self.reg_btn = QPushButton("Sign Up Now")
        self.reg_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
        layout.addWidget(self.reg_btn)

        self.back_btn = QPushButton("Already have an account? Log in")
        self.back_btn.setStyleSheet("background: transparent; color: #f5e0dc; text-decoration: underline;")
        self.back_btn.clicked.connect(self.switch_to_login.emit)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)