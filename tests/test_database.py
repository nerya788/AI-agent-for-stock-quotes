import os
import requests
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def check_dependencies():
    print("🔍 1. Checking installations...")
    try:
        import fastapi
        import supabase
        import yfinance
        print("✅ All libraries are installed correctly.")
    except ImportError as e:
        print(f"❌ Missing library: {e}. Run: pip install -r requirements.txt")

def check_supabase():
    print("\n☁️ 2. Checking cloud connection (Supabase)...")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Supabase keys are missing in the .env file")
        return

    try:
        supabase = create_client(url, key)
        # Simple read attempt from the table we created
        supabase.table("stocks_watchlist").select("id").limit(1).execute()
        print("✅ Connection to Supabase is valid!")
    except Exception as e:
        print(f"❌ Error connecting to cloud: {e}")

if __name__ == "__main__":
    print("=== Final Project: System Integrity Check ===\n")
    check_dependencies()
    check_supabase()