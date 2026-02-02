from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.repositories.auth_repository import AuthRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_repo = AuthRepository()

# מודל הנתונים (נשאר זהה)
class UserAuth(BaseModel):
    email: str
    password: str
    full_name: str = None

@router.post("/register")
async def register(user: UserAuth):
    try:
        print(f"📡 Auth Routes: Register request for {user.email}")
        # שימוש ב-Supabase Authentication
        response = auth_repo.register_user(user.email, user.password, user.full_name)
        
        if response.user:
            return {
                "status": "success", 
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": user.full_name or response.user.user_metadata.get("full_name", "User")
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except Exception as e:
        print(f"❌ Register error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user: UserAuth):
    try:
        print(f"📡 Auth Routes: Login request for {user.email}")
        # שימוש ב-Supabase Authentication
        response = auth_repo.login_user(user.email, user.password)
        
        if response.user:
            return {
                "status": "success",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name", "User")
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))