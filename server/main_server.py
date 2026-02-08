from fastapi import FastAPI
import uvicorn
from server.api import auth_routes, stock_routes, trade_routes # ייבוא הראוטרים שיצרנו

app = FastAPI(title="Stock Quotes Enterprise API")

# חיבור הראוטרים לאפליקציה הראשית
app.include_router(auth_routes.router)
app.include_router(stock_routes.router)
app.include_router(trade_routes.router)

@app.get("/")
async def root():
    return {
        "system": "Enterprise Stock System",
        "architecture": "N-Tier Decoupled", # קריצה למרצה ;)
        "status": "Online"
    }

# --- התיקון הקריטי: הרצת השרת ---
if __name__ == "__main__":
    print("🚀 Starting Server on http://127.0.0.1:8000")
    # הפקודה הזו "תופסת" את הטרמינל ולא משחררת אותו
    uvicorn.run(app, host="127.0.0.1", port=8000)