from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor

class LoginView(QWidget):
    # סיגנל שמודיע למנהל המערכת לעבור לדף רישום
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

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        layout.addWidget(self.email_input)

        # שדה סיסמה עם אייקון עין בתוך ה- QLineEdit
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("QLineEdit { color: #d3d3d3; }")
        # פעולה עם אייקון (מצוייר מאימוג'י) בתוך השדה (בצד ימין)
        self.eye_action = QAction(self._create_eye_icon("🙈"), "", self.pass_input)
        self.eye_action.triggered.connect(self.toggle_password_visibility)
        self.pass_input.addAction(self.eye_action, QLineEdit.TrailingPosition)
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

    def toggle_password_visibility(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.eye_action.setIcon(self._create_eye_icon("👁"))
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.eye_action.setIcon(self._create_eye_icon("🙈"))

    def _create_eye_icon(self, char: str) -> QIcon:
        """יוצר אייקון קטן מאימוג'י (עין/קוף) בצבע אפור בהיר."""
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.transparent)
        p = QPainter(pixmap)
        p.setPen(QColor("#d3d3d3"))
        font = p.font()
        font.setPointSize(11)
        p.setFont(font)
        p.drawText(pixmap.rect(), Qt.AlignCenter, char)
        p.end()
        return QIcon(pixmap)

    def reset_password_visibility(self):
        """מאפס את מצב שדה הסיסמה לברירת מחדל: מוסתר + אייקון מכוסה."""
        self._password_visible = False
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.eye_action.setIcon(self._create_eye_icon("🙈"))