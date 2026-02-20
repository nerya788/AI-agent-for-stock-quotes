from fastapi import FastAPI
import uvicorn
from server.api import (
    auth_routes,
    stock_routes,
    trade_routes,
)  # Import the routers we created

app = FastAPI(title="Stock Quotes Enterprise API")

# Attach routers to the main application
app.include_router(auth_routes.router)
app.include_router(stock_routes.router)
app.include_router(trade_routes.router)


@app.get("/")
async def root():
    return {
        "system": "Enterprise Stock System",
        "architecture": "N-Tier Decoupled",
        "status": "Online",
    }


# --- Run server ---
if __name__ == "__main__":
    print("🚀 Starting Server on http://127.0.0.1:8000")
    # This command blocks the terminal while the server is running
    uvicorn.run(app, host="127.0.0.1", port=8000)
