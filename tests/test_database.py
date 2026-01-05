import os
import requests
from dotenv import load_dotenv
from supabase import create_client

# טעינת משתני סביבה
load_dotenv()

def check_dependencies():
    print("🔍 1. בודק התקנות...")
    try:
        import fastapi
        import supabase
        import yfinance
        print("✅ כל הספריות מותקנות כשורה.")
    except ImportError as e:
        print(f"❌ חסרה ספרייה: {e}. הרץ: pip install -r requirements.txt")

def check_supabase():
    print("\n☁️ 2. בודק חיבור לענן (Supabase)...")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ שגיאה: מפתחות Supabase חסרים בקובץ ה-.env")
        return

    try:
        supabase = create_client(url, key)
        # ניסיון קריאה פשוט מהטבלה שיצרנו
        supabase.table("stocks_watchlist").select("id").limit(1).execute()
        print("✅ החיבור ל-Supabase תקין!")
    except Exception as e:
        print(f"❌ שגיאה בחיבור לענן: {e}")

if __name__ == "__main__":
    print("=== פרויקט סיום: בדיקת תקינות מערכת ===\n")
    check_dependencies()
    check_supabase()