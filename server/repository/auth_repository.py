import os
from supabase import create_client

class AuthRepository:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(url, key)

    def register_user(self, email, password, full_name):
        data = {
            "email": email, 
            "password_hash": password, 
            "full_name": full_name
        }
        return self.supabase.table("users").insert(data).execute()

    def get_user_by_email(self, email):
        return self.supabase.table("users").select("*").eq("email", email).execute()