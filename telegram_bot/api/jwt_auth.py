from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from telegram_bot.config import ADMIN_CHAT_ID
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["auth"])

class Settings(BaseModel):
    authjwt_secret_key: str = "super-secret-key"  # Лучше вынести в env

@AuthJWT.load_config
def get_config():
    return Settings()

class LoginModel(BaseModel):
    admin_id: int

@router.post("/login")
def login(data: LoginModel, Authorize: AuthJWT = Depends()):
    if data.admin_id != int(ADMIN_CHAT_ID):
        raise HTTPException(status_code=401, detail="Not authorized")
    access_token = Authorize.create_access_token(subject=str(data.admin_id))
    return {"access_token": access_token}

@router.get("/protected")
def protected(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Not authorized")
    return {"msg": "You are authorized"} 