# DAL: Data Access Layer - שכבה טכנית בלבד [cite: 23]
import os
from supabase import create_client

class SupabaseDAL:
    def __init__(self):
        self.client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    def select(self, table: str, query: dict):
        # ביצוע שאילתה גולמית
        return self.client.table(table).select("*").match(query).execute()

    def insert(self, table: str, data: dict):
        return self.client.table(table).insert(data).execute()