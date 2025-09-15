from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
import service
from schemas import UserReadRequest, UserReadResponse, UserUpdateRequest, UserUpdateResponse, UserDeleteRequest, UserDeleteResponse, ErrorResponse


users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/",
        response_model=list[UserReadResponse], 
        tags=["Users"], 
        summary="Получить всех пользователей", 
        description="Возвращает список всех пользователей в системе")
async def get_users(session: AsyncSession = Depends(get_session)):
    user_service = service.UserService()
    return await user_service.get_all_users(session=session)

@users_router.get("/{user_id}",
        response_model=UserReadResponse,
        tags=["Users"], 
        summary="Получить пользователя по ID", 
        description="Возвращает данные пользователя по его ID",
        responses={
            404: {"model": ErrorResponse, "description": "Пользователь не найден"}
        })
async def get_user(user_id: int = Path(..., title="ID пользователя", description="Уникальный идентификатор пользователя"), session: AsyncSession = Depends(get_session)):
    user_service = service.UserService()
    return await user_service.get_user_by_id(user_id, session=session)

@users_router.put("/{user_id}",
         response_model=UserUpdateResponse,
         tags=["Users"], 
         summary="Обновить пользователя", 
         description="Обновляет данные существующего пользователя",
         responses={
             404: {"model": ErrorResponse, "description": "Пользователь не найден"},
             409: {"model": ErrorResponse, "description": "Пользователь с таким email или username уже существует"}
         })
async def update_user(user_data: UserUpdateRequest, 
                     user_id: int = Path(...,  title="ID пользователя",
                                         description="Уникальный идентификатор пользователя"), session: AsyncSession = Depends(get_session)):
    user_service = service.UserService()
    return await user_service.update_user(user_id, user_data, session=session)

@users_router.delete("/{user_id}",
            response_model=UserDeleteResponse,
            tags=["Users"], 
            summary="Удалить пользователя", 
            description="Удаляет пользователя из системы по его ID",
            responses={
                404: {"model": ErrorResponse, "description": "Пользователь не найден"}
            })
async def delete_user(user_id: int = Path(...,  title="ID пользователя",
                                          description="Уникальный идентификатор пользователя"), session: AsyncSession = Depends(get_session)):
    user_service = service.UserService()
    return await user_service.delete_user(user_id, session=session)