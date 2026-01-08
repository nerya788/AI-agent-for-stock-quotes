import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class SupabaseDAL:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("ERROR: Supabase credentials missing in .env")
            cls._instance = create_client(url, key)
            print("✅ Supabase connection established (DAL Layer)")
        return cls._instance
    
    def select(self, table: str, query: dict):
        return self.get_instance().table(table).select("*").match(query).execute()

    def insert(self, table: str, data: dict):
        return self.get_instance().table(table).insert(data).execute()