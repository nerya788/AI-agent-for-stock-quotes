import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


class AuthRepository:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.dal = create_client(url, key)

    def register_user(self, email, password, full_name=None):
        """
        Register a user using Supabase Authentication.
        """
        try:
            print(f"🔐 AuthRepository: Registering {email} via Supabase Auth...")
            # Use Supabase Auth API
            response = self.dal.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"full_name": full_name or ""}},
                }
            )
            print(
                f"✅ User registered: {response.user.email if response.user else 'error'}"
            )
            return response
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            raise Exception(f"Registration failed: {str(e)}")

    def login_user(self, email, password):
        """
        Log in a user using Supabase Authentication.
        """
        try:
            print(f"🔐 AuthRepository: Logging in {email} via Supabase Auth...")
            response = self.dal.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            print(
                f"✅ User logged in: {response.user.email if response.user else 'error'}"
            )
            return response
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            raise Exception(f"Login failed: {str(e)}")
