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

def check_fastapi():
    print("\n🚀 3. בודק שרת FastAPI (Gateway)...")
    try:
        # בדיקה אם השרת מגיב בפורט שהגדרנו (8000 או 8001)
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if response.status_code == 200:
            print("✅ שרת ה-Gateway פועל ומגיב!")
    except requests.exceptions.ConnectionError:
        print("❌ שרת ה-FastAPI לא פועל. וודא שהרצת את main.py")

if __name__ == "__main__":
    print("=== פרויקט סיום: בדיקת תקינות מערכת ===\n")
    check_dependencies()
    check_fastapi()