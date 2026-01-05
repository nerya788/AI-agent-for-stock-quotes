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

def check_fastapi():
    print("\n🚀 3. Checking FastAPI server (Gateway)...")
    try:
        # Check if the server responds on the port we configured (8000 or 8001)
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if response.status_code == 200:
            print("✅ Gateway server is running and responding!")
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI server is not running. Make sure you ran main.py")

if __name__ == "__main__":
    print("=== Final Project: System Integrity Check ===\n")
    check_dependencies()
    check_fastapi()