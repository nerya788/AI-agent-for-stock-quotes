from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal

class RegisterView(QWidget):
    switch_to_login = Signal()

    def __init__(self):
        super().__init__()
        self._password_visible = False
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

        # password field with built-in toggle button
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("QLineEdit { color: #d3d3d3; }")

        self.pass_input.setTextMargins(0, 0, 50, 0)
        self.toggle_btn = QPushButton("Show", self.pass_input)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet("background: transparent; color: #d3d3d3; font-weight: bold; font-size: 14px; border: none;")
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)

        le_layout = QHBoxLayout(self.pass_input)
        le_layout.setContentsMargins(0, 0, 10, 0)
        le_layout.addWidget(self.toggle_btn, 0, Qt.AlignRight)

        layout.addWidget(self.pass_input)

        self.reg_btn = QPushButton("Sign Up Now")
        self.reg_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
        layout.addWidget(self.reg_btn)

        self.back_btn = QPushButton("Already have an account? Log in")
        self.back_btn.setStyleSheet("background: transparent; color: #f5e0dc; text-decoration: underline;")
        self.back_btn.clicked.connect(self.switch_to_login.emit)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("Hide")
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("Show")

    def reset_password_visibility(self):
        self._password_visible = False
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.toggle_btn.setText("Show")