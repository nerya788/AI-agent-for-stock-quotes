import os
from dotenv import load_dotenv
from supabase import create_client, Client

# טעינת משתני הסביבה מקובץ ה-.env
load_dotenv()

def run_connection_test():
    # שליפת המשתנים
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ שגיאה: וודא ש-SUPABASE_URL ו-SUPABASE_KEY מוגדרים ב-.env")
        return

    try:
        # יצירת הלקוח של Supabase
        supabase: Client = create_client(url, key)
        print("✅ החיבור ל-SDK של Supabase הוגדר בהצלחה!")

        # ביצוע הרשמה (Sign Up) כדי ש-Supabase יזהה את החיבור הראשון
        # זה בדיוק מה שהם ביקשו באתר כדי להשלים את ה-Installation
        test_email = "nerya_test@gmail.com"
        test_password = "123456"

        response = supabase.auth.sign_up({
            "email": test_email,
            "password": test_password,
        })

        print(f"🚀 נשלחה בקשת הרשמה עבור: {test_email}")
        print("בדוק עכשיו את האתר של Supabase - המסך אמור להשתנות ל-Dashboard!")

    except Exception as e:
        print(f"❌ שגיאה במהלך החיבור: {e}")

if __name__ == "__main__":
    run_connection_test()