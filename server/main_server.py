from fastapi import FastAPI
from server.api import auth_routes, stock_routes # ייבוא הראוטרים שיצרנו

app = FastAPI(title="Stock Quotes Enterprise API")

# חיבור הראוטרים לאפליקציה הראשית
app.include_router(auth_routes.router)
app.include_router(stock_routes.router)

@app.get("/")
async def root():
    return {
        "system": "Enterprise Stock System",
        "architecture": "N-Tier Decoupled", # קריצה למרצה ;)
        "status": "Online"
    }