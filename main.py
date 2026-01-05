# תוכן אפשרי ל-main.py הראשי
import uvicorn

if __name__ == "__main__":
    uvicorn.run("server.main_server:app", host="127.0.0.1", port=8000, reload=True)