from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal

class LoginView(QWidget):
    switch_to_register = Signal()

    def __init__(self):
        super().__init__()
        self._password_visible = False
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

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f38ba8; font-size: 13px; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # הגדרות העיצוב
        self._input_base_style = (
            "QLineEdit {"
            "background-color: #313244;"
            "color: #ffffff;"
            "border: 1px solid #45475a;"
            "border-radius: 8px;"
            "padding: 8px;"
            "}"
            "QLineEdit:focus {"
            "border: 1px solid #89b4fa;"
            "}"
        )
        self._input_error_style = (
            "QLineEdit {"
            "background-color: #313244;"
            "color: #ffffff;"
            "border: 2px solid #f38ba8;"
            "border-radius: 8px;"
            "padding: 7px;"
            "}"
        )

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.email_input.setStyleSheet(self._input_base_style)
        self.email_input.textChanged.connect(self.clear_error)
        layout.addWidget(self.email_input)

        # password field with built-in toggle button
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet(self._input_base_style)
        self.pass_input.textChanged.connect(self.clear_error)

        # text margins to make room for the toggle button
        self.pass_input.setTextMargins(0, 0, 50, 0)
        self.toggle_btn = QPushButton("Show", self.pass_input)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet("background: transparent; color: #a6adc8; font-weight: bold; font-size: 14px; border: none;")
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)

        # Layout for the password field and toggle button
        le_layout = QHBoxLayout(self.pass_input)
        le_layout.setContentsMargins(0, 0, 10, 0)
        le_layout.addWidget(self.toggle_btn, 0, Qt.AlignRight)

        layout.addWidget(self.pass_input)

        self.login_btn = QPushButton("Sign In")
        layout.addWidget(self.login_btn)

        self.go_to_reg_btn = QPushButton("New here? Create an account")
        self.go_to_reg_btn.setStyleSheet("background: transparent; color: #f5e0dc; text-decoration: underline;")
        self.go_to_reg_btn.setCursor(Qt.PointingHandCursor)
        self.go_to_reg_btn.clicked.connect(self.switch_to_register.emit)
        layout.addWidget(self.go_to_reg_btn)

        self.setLayout(layout)

    def set_error(self, message: str, highlight_fields: bool = True):
        self.error_label.setText(message)
        self.error_label.show()
        if highlight_fields:
            self.email_input.setStyleSheet(self._input_error_style)
            self.pass_input.setStyleSheet(self._input_error_style)

    def clear_error(self):
        if self.error_label.isVisible():
            self.error_label.hide()
            self.error_label.setText("")
        self.email_input.setStyleSheet(self._input_base_style)
        self.pass_input.setStyleSheet(self._input_base_style)

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