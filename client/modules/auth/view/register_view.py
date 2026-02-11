from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor

class RegisterView(QWidget):
    # סיגנל לחזרה לכניסה
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

        # שדה סיסמה עם אייקון עין בתוך ה- QLineEdit
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("QLineEdit { color: #d3d3d3; }")
        self.eye_action = QAction(self._create_eye_icon("🙈"), "", self.pass_input)
        self.eye_action.triggered.connect(self.toggle_password_visibility)
        self.pass_input.addAction(self.eye_action, QLineEdit.TrailingPosition)
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