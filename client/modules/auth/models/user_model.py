class UserModel:
    def __init__(self, id: str, email: str, full_name: str, token: str = None):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.token = token

    @classmethod
    def from_json(cls, data: dict):
        """Convert the server response (JSON) into a user object."""
        return cls(
            id=data.get("id"),
            email=data.get("email"),
            full_name=data.get("full_name", "Unknown"),  # Default if no name
            token=data.get("access_token"),  # For future use
        )
