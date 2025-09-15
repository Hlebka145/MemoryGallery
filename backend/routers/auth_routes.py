from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas import UserCreateRequest, UserCreateResponse, Token, TokenRefresh, CSRFToken
from service import UserService
import auth_utils

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register",
            response_model=list[UserCreateResponse],
            tags=["Auth"], 
            summary="Регистрация пользователя")
async def register(user_data: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Регистрация нового пользователя"""
    user_service = UserService()
    result = await user_service.create_user(user_data, session=session)
    return result

@router.post("/login",
            tags=["Auth"],
            response_model=Token,
            summary="Логин по email и паролю",
            description="В поле username указывайте email. Это ограничение OAuth2PasswordRequestForm.")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user_service = UserService()
    # username = email (по стандарту OAuth2PasswordRequestForm)
    user = await user_service.authenticate_user(form_data.username, form_data.password, session=session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = auth_utils.create_access_token(user.email)
    refresh_token = auth_utils.create_refresh_token(user.email)
    await user_service.update_user_refresh_token(user.email, refresh_token, session=session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh",
            tags=["Auth"],
            response_model=Token)
async def refresh_token(token_data: TokenRefresh, session: AsyncSession = Depends(get_session)):
    """Обновление refresh-токена"""
    payload = auth_utils.decode_token(token_data.refresh_token, token_type="refresh")
    user_service = UserService()
    user = await user_service.get_user_by_email(payload["sub"], session=session)
    if not user or user.refresh_token != token_data.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = auth_utils.create_access_token(user.email)
    refresh_token = auth_utils.create_refresh_token(user.email)
    await user_service.update_user_refresh_token(user.email, refresh_token, session=session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout",
            tags=["Auth"],
            summary="Выход из системы")
async def logout(request: Request, session: AsyncSession = Depends(get_session)):
    """Выход из системы"""
    # Получаем пользователя из access_token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = auth_utils.decode_token(token, token_type="access")
    user_service = UserService()
    await user_service.update_user_refresh_token(payload["sub"], None, session=session)
    return {"message": "Logged out"}

@router.get("/csrf-token",
            response_model=CSRFToken,
            tags=["Auth"],
            summary="CSRF Token")
async def get_csrf_token():
    """Создание и получение csrf-токена"""
    csrf_token = auth_utils.create_csrf_token()
    return {"csrf_token": csrf_token}