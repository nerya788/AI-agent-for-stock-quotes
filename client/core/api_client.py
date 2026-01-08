import requests

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def login(self, email, password):
            try:
                # וודא שהנתיב הוא /auth/login ולא סתם /login
                response = requests.post(f"{self.base_url}/auth/login", json={
                    "email": email,
                    "password": password
                })
                if response.status_code == 200:
                    return response.json()
                return {"status": "error", "detail": response.text}
            except Exception as e:
                return {"status": "error", "detail": str(e)}

    def register(self, email, password, full_name):
        response = requests.post(f"{self.base_url}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": full_name
        })
        return response.json()