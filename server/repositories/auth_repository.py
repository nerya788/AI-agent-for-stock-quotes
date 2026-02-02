import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class AuthRepository:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(url, key)

    def register_user(self, email, password, full_name=None):
        """
        רישום משתמש באמצעות Supabase Authentication
        """
        try:
            print(f"🔐 AuthRepository: Registering {email} via Supabase Auth...")
            # שימוש ב-Auth API של Supabase
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name or ""
                    }
                }
            })
            print(f"✅ User registered: {response.user.email if response.user else 'error'}")
            return response
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            raise Exception(f"Registration failed: {str(e)}")

    def login_user(self, email, password):
        """
        התחברות משתמש באמצעות Supabase Authentication
        """
        try:
            print(f"🔐 AuthRepository: Logging in {email} via Supabase Auth...")
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            print(f"✅ User logged in: {response.user.email if response.user else 'error'}")
            return response
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            raise Exception(f"Login failed: {str(e)}")