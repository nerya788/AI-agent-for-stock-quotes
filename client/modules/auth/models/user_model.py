class UserModel:
    def __init__(self, email: str, full_name: str, token: str = None):
        self.email = email
        self.full_name = full_name
        self.token = token

    @classmethod
    def from_json(cls, data: dict):
        """הופך את התשובה מהשרת (JSON) לאובייקט משתמש"""
        return cls(
            email=data.get("email"),
            full_name=data.get("full_name", "Unknown"), # ברירת מחדל אם אין שם
            token=data.get("access_token") # הכנה לעתיד
        )