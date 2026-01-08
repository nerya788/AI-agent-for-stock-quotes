# Repository: ממיר מידע גולמי לאובייקטים עסקיים [cite: 19]
from server.dal.supabase_client import SupabaseDAL

class UserRepository:
    def __init__(self):
        self.dal = SupabaseDAL() # הזרקת תלות

    def create_user(self, email, password, name):
            user_data = {
                "email": email, 
                "password_hash": password, 
                "full_name": name
            }
            # שימוש בפונקציית העזר הגנרית insert
            return self.dal.insert("users", user_data)

    def find_user_by_email(self, email):
        # שימוש בפונקציית העזר הגנרית select
        result = self.dal.select("users", {"email": email})
        return result.data[0] if result.data else None