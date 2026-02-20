from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from client.modules.auth.view.login_view import LoginView
from client.modules.auth.view.register_view import RegisterView
from client.core.api_client import APIClient
from client.modules.auth.models.user_model import UserModel
from client.core.worker_thread import WorkerThread  # <--- our turbo


class AuthController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.api = APIClient()
        self.worker = None  # Worker thread reference

        # Internal view management
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.login_view = LoginView()
        self.register_view = RegisterView()

        # Start with login
        self.current_view = self.login_view
        self.layout.addWidget(self.current_view)

        self.setup_connections()

    def setup_connections(self):
        # Internal navigation
        self.login_view.switch_to_register.connect(self.show_register)
        self.register_view.switch_to_login.connect(self.show_login)

        # Server actions
        self.login_view.login_btn.clicked.connect(self.handle_login)
        self.register_view.reg_btn.clicked.connect(self.handle_register)

    def show_register(self):
        self.layout.removeWidget(self.current_view)
        self.current_view.hide()
        self.current_view = self.register_view
        self.layout.addWidget(self.current_view)
        self.current_view.show()

    def show_login(self):
        self.layout.removeWidget(self.current_view)
        self.current_view.hide()
        self.current_view = self.login_view
        self.layout.addWidget(self.current_view)
        self.current_view.show()

    # --- Background tasks ---

    def _login_task(self, email, password):
        """Perform login against the server in the background."""
        return self.api.login(email, password)

    def _register_task(self, email, password, full_name):
        """Perform registration against the server in the background."""
        return self.api.register(email, password, full_name)

    # --- Login logic ---

    def handle_login(self):
        email = self.login_view.email_input.text()
        password = self.login_view.pass_input.text()

        if not email or not password:
            QMessageBox.warning(self, "שגיאה", "נא למלא את כל השדות")
            return

        # Update UI - disable button and change text
        self.login_view.login_btn.setEnabled(False)
        self.login_view.login_btn.setText("מתחבר... ⏳")

        # Start worker
        self.worker = WorkerThread(self._login_task, email, password)
        self.worker.finished.connect(self.on_login_complete)
        self.worker.error.connect(self.on_auth_error)
        self.worker.start()

    def on_login_complete(self, response):
        """Handle the server response after login."""
        # Restore button state
        self.login_view.login_btn.setEnabled(True)
        self.login_view.login_btn.setText("Login")

        if response and response.get("status") == "success":
            try:
                user_data = response.get("user", {})
                user_model = UserModel.from_json(user_data)

                print(f"✅ Login Successful! User: {user_model.full_name}")
                self.app.set_user_session(user_model)
                self.app.navigate_to_portfolio()
            except Exception as e:
                QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד נתוני משתמש: {e}")
        else:
            error_msg = response.get("detail", "Login failed")
            QMessageBox.warning(self, "שגיאת התחברות", str(error_msg))

    # --- Registration logic ---

    def handle_register(self):
        full_name = self.register_view.name_input.text()
        email = self.register_view.email_input.text()
        password = self.register_view.pass_input.text()

        if not email or not password or not full_name:
            QMessageBox.warning(self, "שגיאה", "נא למלא את כל השדות")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "שגיאה", "הסיסמה חייבת להכיל לפחות 6 תווים")
            return

        # Update UI
        self.register_view.reg_btn.setEnabled(False)
        self.register_view.reg_btn.setText("נרשם... ⏳")

        # Start worker
        self.worker = WorkerThread(self._register_task, email, password, full_name)
        self.worker.finished.connect(self.on_register_complete)
        self.worker.error.connect(self.on_auth_error)
        self.worker.start()

    def on_register_complete(self, response):
        """Handle the server response after registration."""
        self.register_view.reg_btn.setEnabled(True)
        self.register_view.reg_btn.setText("Register")

        if response and response.get("status") == "success":
            QMessageBox.information(
                self, "הצלחה! 🎉", "ההרשמה בוצעה בהצלחה!\nכעת ניתן להתחבר."
            )
            self.show_login()
        else:
            error_msg = response.get("detail", "Registration failed")
            QMessageBox.warning(self, "שגיאת רישום", str(error_msg))

    def on_auth_error(self, error_msg):
        """Handle general communication errors."""
        # Re-enable buttons on both screens in case of an error
        self.login_view.login_btn.setEnabled(True)
        self.login_view.login_btn.setText("Login")
        self.register_view.reg_btn.setEnabled(True)
        self.register_view.reg_btn.setText("Register")

        QMessageBox.critical(self, "שגיאת תקשורת", f"לא ניתן להתחבר לשרת:\n{error_msg}")
