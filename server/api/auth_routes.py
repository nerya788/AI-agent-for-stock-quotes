from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

user_repo = UserRepository()

# מודל הנתונים (נשאר זהה)
class UserAuth(BaseModel):
    email: str
    password: str
    full_name: str = None

@router.post("/register")
async def register(user: UserAuth):
    try:
        # פנייה ל-Repository שיצרנו קודם
        result = user_repo.create_user(user.email, user.password, user.full_name)
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user: UserAuth):
    # שים לב: כאן הוספנו לוגיקה שהייתה ב-Main הישן
    found_user = user_repo.find_user_by_email(user.email)
    
    if not found_user: 
        raise HTTPException(status_code=401, detail="User not found")
        
    # בדיקת סיסמה (בפרויקט אמיתי עושים כאן Verify Hash)
    if found_user['password_hash'] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return {"status": "success", "user": found_user}