from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from client.modules.auth.view.login_view import LoginView
from client.modules.auth.view.register_view import RegisterView
from client.core.api_client import APIClient
# וודא שהמודל קיים במיקום הזה
from client.modules.auth.models.user_model import UserModel

class AuthController(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller # רפרנס לאפליקציה הראשית
        self.api = APIClient()
        
        # ניהול פנימי של ה-Views בתוך המודול הזה
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.login_view = LoginView()
        self.register_view = RegisterView()
        
        # מתחילים עם לוגין
        self.current_view = self.login_view
        self.layout.addWidget(self.current_view)
        
        self.setup_connections()

    def setup_connections(self):
        # מעברים פנימיים (Login <-> Register)
        self.login_view.switch_to_register.connect(self.show_register)
        self.register_view.switch_to_login.connect(self.show_login)
        
        # פעולות מול השרת
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

    def handle_login(self):
        email = self.login_view.email_input.text()
        password = self.login_view.pass_input.text()
        
        # 1. ולידציה בסיסית
        if not email or not password:
            QMessageBox.warning(self, "שגיאה", "נא למלא את כל השדות")
            return

        print(f"📡 Auth Controller: Sending login request for {email}...")
        
        try:
            # 2. שליחה לשרת
            response = self.api.login(email, password)
            
            # 3. בדיקת הצלחה
            if response and response.get("status") == "success":
                # --- כאן השינוי הגדול (MVC) ---
                
                # א. המרת המידע הגולמי למודל חכם
                user_data = response.get("user", {})
                user_model = UserModel.from_json(user_data)
                
                print(f"✅ Login Successful! User: {user_model.full_name}")
                
                # ב. עדכון ה-Session באפליקציה הראשית
                self.app.set_user_session(user_model)
                
                # ג. מעבר מסך
                self.app.navigate_to_portfolio()
            else:
                # כישלון בהתחברות (סיסמה שגויה וכו')
                error_msg = response.get("detail", "Login failed")
                print(f"❌ Login Failed: {error_msg}")
                QMessageBox.warning(self, "שגיאת התחברות", str(error_msg))
                
        except Exception as e:
            # שגיאת רשת או קריסה
            print(f"❌ Connection Error: {e}")
            QMessageBox.critical(self, "שגיאת מערכת", f"לא ניתן להתחבר לשרת:\n{e}")

    def handle_register(self):
        # לוגיקה לרישום (אפשר להרחיב בהמשך)
        email = self.register_view.email_input.text()
        print(f"Auth Module: Registering {email}...")
        # כרגע נחזיר אותו ללוגין אחרי לחיצה
        self.show_login()