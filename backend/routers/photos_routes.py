from fastapi import APIRouter, Depends, HTTPException, status, Path, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
import service
import uuid
import json
from schemas import PhotoCreateRequest, PhotoCreateResponse, PhotoReadRequest, PhotoReadResponse, PhotoUpdateRequest, PhotoUpdateResponse, PhotoDeleteRequest, PhotoDeleteResponse, ErrorResponse


photos_router = APIRouter(prefix="/photos", tags=["Photos"])

@photos_router.post("/",
        response_model=PhotoCreateResponse,
        tags=["Photos"],
        summary="Загрузить фото",
        description="Загрузка фото в систему")
async def upload_photo(photo_data_json: str = Form(...), file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    # Парсим JSON обратно в модель для валидации
    photo_data_dict = json.loads(photo_data_json)
    photo_data = PhotoCreateRequest(**photo_data_dict)

    photo_service = service.PhotoService()
    return await photo_service.upload_photo(photo_data, file=file, session=session)

@photos_router.get("/",
        response_model=list[PhotoReadResponse], 
        tags=["Photos"], 
        summary="Получить все фото", 
        description="Возвращает список всех фото в системе")
async def get_photos(session: AsyncSession = Depends(get_session)):
    photo_service = service.PhotoService()
    return await photo_service.get_all_photos(session=session)

@photos_router.get("/{photo_id}",
        response_model=PhotoReadResponse,
        tags=["Photos"], 
        summary="Получить фото по ID", 
        description="Возвращает данные фото по его ID",
        responses={
            404: {"model": ErrorResponse, "description": "Фото не найдено"}
        })
async def get_photo(photo_id: int = Path(..., title="ID фото", description="Уникальный идентификатор фото"), session: AsyncSession = Depends(get_session)):
    photo_service = service.PhotoService()
    return await photo_service.get_photo_by_id(photo_id, session=session)

@photos_router.put("/{photo_id}",
        response_model=PhotoUpdateResponse,
        tags=["Photos"], 
        summary="Обновить фото", 
        description="Обновляет данные существующего фото",
        responses={
            404: {"model": ErrorResponse, "description": "Фото не найдено"}
        })
async def update_photo(photo_data: PhotoUpdateRequest, 
                    photo_id: int = Path(...,  title="ID фото",
                                        description="Уникальный идентификатор фото"), session: AsyncSession = Depends(get_session)):
    photo_service = service.PhotoService()
    return await photo_service.update_photo(photo_id, photo_data, session=session)

@photos_router.put("/{photo_id}",
        response_model=PhotoUpdateResponse,
        tags=["Photos"], 
        summary="Обновить фото", 
        description="Обновляет данные существующего фото",
        responses={
            404: {"model": ErrorResponse, "description": "Фото не найдено"}
        })
async def update_photo(photo_data: PhotoUpdateRequest, 
                    photo_id: int = Path(...,  title="ID фото",
                                        description="Уникальный идентификатор фото"), session: AsyncSession = Depends(get_session)):
    photo_service = service.PhotoService()
    return await photo_service.update_photo(photo_id, photo_data, session=session)

@photos_router.delete("/{photo_id}",
            response_model=PhotoDeleteResponse,
            tags=["Photos"], 
            summary="Удалить фото", 
            description="Удаляет фото из системы по его ID",
            responses={
                404: {"model": ErrorResponse, "description": "Фото не найдено"}
            })
async def delete_photo(photo_id: int = Path(...,  title="ID фото",
                                        description="Уникальный идентификатор фото"), session: AsyncSession = Depends(get_session)):
    photo_service = service.PhotoService()
    photo = await photo_service.get_photo_by_id(photo_id, session=session)
    return await photo_service.delete_photo(photo_id, photo.path, session=session)