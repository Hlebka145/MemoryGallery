from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas import (
    UserCreateRequest, Token, TokenRefresh, CSRFToken,
    EmailVerificationRequest, EmailVerificationResponse,
    ResendVerificationRequest, ResendVerificationResponse
)
from service import UserService
import auth_utils

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user_data: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Регистрация нового пользователя с отправкой кода подтверждения на email"""
    user_service = UserService()
    result = await user_service.create_user(user_data, session=session)
    return result

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    verification_data: EmailVerificationRequest, 
    session: AsyncSession = Depends(get_session)
):
    """Подтверждение email по коду"""
    user_service = UserService()
    user = await user_service.verify_email(
        email=verification_data.email,
        verification_code=verification_data.verification_code,
        session=session
    )
    
    # Создаем JWT токены после подтверждения
    access_token = auth_utils.create_access_token(user.email)
    refresh_token = auth_utils.create_refresh_token(user.email)
    
    # Сохраняем refresh_token в базе
    await user_service.update_user_refresh_token(user.email, refresh_token, session=session)
    
    return EmailVerificationResponse(
        success=True,
        message="Email подтвержден успешно",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    resend_data: ResendVerificationRequest,
    session: AsyncSession = Depends(get_session)
):
    """Повторная отправка кода подтверждения"""
    user_service = UserService()
    result = await user_service.resend_verification_code(
        email=resend_data.email,
        session=session
    )
    
    return ResendVerificationResponse(
        success=True,
        message=result["message"]
    )

@router.post("/login", response_model=Token, summary="Логин по email и паролю", description="В поле username указывайте email. Это ограничение OAuth2PasswordRequestForm.")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user_service = UserService()
    # username = email (по стандарту OAuth2PasswordRequestForm)
    user = await user_service.authenticate_user(form_data.username, form_data.password, session=session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Проверяем, подтвержден ли email
    if not user.email_verified:
        raise HTTPException(
            status_code=401, 
            detail="Email не подтвержден. Проверьте почту или запросите новый код подтверждения."
        )
    
    access_token = auth_utils.create_access_token(user.email)
    refresh_token = auth_utils.create_refresh_token(user.email)
    await user_service.update_user_refresh_token(user.email, refresh_token, session=session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, session: AsyncSession = Depends(get_session)):
    payload = auth_utils.decode_token(token_data.refresh_token, token_type="refresh")
    user_service = UserService()
    user = await user_service.get_user_by_email(payload["sub"], session=session)
    if not user or user.refresh_token != token_data.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = auth_utils.create_access_token(user.email)
    refresh_token = auth_utils.create_refresh_token(user.email)
    await user_service.update_user_refresh_token(user.email, refresh_token, session=session)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(request: Request, session: AsyncSession = Depends(get_session)):
    # Получаем пользователя из access_token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = auth_utils.decode_token(token, token_type="access")
    user_service = UserService()
    await user_service.update_user_refresh_token(payload["sub"], None, session=session)
    return {"message": "Logged out"}

@router.get("/csrf-token", response_model=CSRFToken)
async def get_csrf_token():
    csrf_token = auth_utils.create_csrf_token()
    return {"csrf_token": csrf_token}