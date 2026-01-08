import requests

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def login(self, email, password):
        # שליחת בקשה לשרת ה-FastAPI
        response = requests.post(f"{self.base_url}/auth/login", json={
            "email": email,
            "password": password
        })
        return response.json()

    def register(self, email, password, full_name):
        response = requests.post(f"{self.base_url}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": full_name
        })
        return response.json()