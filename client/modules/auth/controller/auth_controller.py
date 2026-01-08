from PySide6.QtWidgets import QWidget, QVBoxLayout
# ייבוא מהמיקומים החדשים
from client.modules.auth.view.login_view import LoginView
from client.modules.auth.view.register_view import RegisterView
from client.core.api_client import APIClient

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
            
            # 1. בדיקת קלט
            if not email or not password:
                print("Error: Missing fields") # או שתשתמש ב-QMessageBox
                return

            print(f"📡 Auth Controller: Sending login request for {email}...")
            
            try:
                # 2. שליחה לשרת האמיתי
                response = self.api.login(email, password)
                
                # 3. בדיקת התשובה
                if response and response.get("status") == "success":
                    print("✅ Login Successful!")
                    user_name = response.get("user", {}).get("full_name", "User")
                    
                    # עדכון השם בדשבורד (דרך ה-AppController)
                    # נניח שיש פונקציה כזו ב-AppController, אם לא - לא נורא כרגע
                    # self.app.set_user_context(user_name)
                    
                    # מעבר לדף הבא
                    self.app.navigate_to_portfolio()
                else:
                    print(f"❌ Login Failed: {response}")
                    # כאן כדאי להקפיץ הודעת שגיאה למשתמש
                    
            except Exception as e:
                print(f"❌ Connection Error: {e}")

    def handle_register(self):
        print("Auth Module: Registering...")
        self.show_login()