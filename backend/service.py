from models.user_model import User
from models.photo_model import Photo
import repository as repository
import schemas as schemas
from fastapi import HTTPException, File, UploadFile
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from auth_utils import hash_password, verify_password
from repository import UserRepository, PhotoRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid


class UserService:
    def __init__(self):
        self.repository = UserRepository()
        
    async def create_user(self, user_data: schemas.UserCreateRequest, session: AsyncSession):        
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password_hashed=await hash_password(user_data.password),
            role=user_data.role,
            is_active=True
        )
        try:
            await self.repository.create(user, session)
        except IntegrityError as e:
            error_msg = str(e.orig)
            if "UNIQUE constraint failed: users.email" in error_msg:
                raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
            else:
                raise HTTPException(status_code=400, detail=f"Ошибка создания пользователя: {error_msg}")
    
    async def get_all_users(self, session: AsyncSession):
        return await self.repository.get_all(session)
    
    async def get_user_by_id(self, user_id: int, session: AsyncSession):
        user = await self.repository.get_by_id(user_id, session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def update_user(self, user_id: int, user_data: schemas.UserUpdateRequest, session: AsyncSession):
        # Преобразуем модель Pydantic в словарь и убираем None значения и id
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None and k != 'id'}
        
        # Хешируем пароль если есть в данных
        if 'password' in update_data:
            update_data['password_hashed'] = await hash_password(update_data.pop('password'))
        
        try:
            updated_user = await self.repository.update(user_id, update_data, session)
            if not updated_user:
                raise HTTPException(status_code=404, detail="User not found")
            return {"message": f"{self.repository.get_model_name()} updated successfully"}
        except IntegrityError as e:
            error_msg = str(e.orig)
            if "UNIQUE constraint failed: users.email" in error_msg:
                raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
            else:
                raise HTTPException(status_code=400, detail=f"Ошибка обновления пользователя: {error_msg}")
    
    async def delete_user(self, user_id: int, session: AsyncSession):
        result = await self.repository.delete(user_id, session)
        if result["message"] == f"{self.repository.get_model_name()} not found":
            raise HTTPException(status_code=404, detail="User not found")
        return result

    async def update_user_refresh_token(self, email: str, refresh_token: str, session: AsyncSession):
        user = await self.repository.get_by_email(email, session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        updated_user = await self.repository.update_refresh_token(user.id, refresh_token, session)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Refresh token updated successfully"}

    async def authenticate_user(self, email: str, password: str, session: AsyncSession):
        user = await self.repository.get_by_email(email, session)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not await verify_password(password, user.password_hashed):
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_by_email(self, email: str, session: AsyncSession):
        return await self.repository.get_by_email(email, session)

class PhotoService:
    def __init__(self):
        self.repository = PhotoRepository()

    async def upload_photo(self, photo_data: schemas.PhotoCreateRequest, file: UploadFile, session: AsyncSession):
        # Проверка на правильность расширения файла
        extensions = [".png", ".jpg", ".jpeg", ".raw", ".tiff"]
        _, file_extension = os.path.splitext(file.filename)
        for ext in extensions:
            if file_extension.lower() == ext:
                break
        else:
            raise HTTPException(status_code=400, detail=f"Invalid photo format")
        
        # Создание пути к файлу и сохранение его на сервер
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("photos", file_name)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        photo = Photo(
            date = photo_data.date,
            path = file_path,
            description = photo_data.description,
            grade = photo_data.grade,
            parallel = photo_data.parallel,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        try:
            await self.repository.create(photo, session)
            return {"message": "Photo uploaded successfully"}
        except IntegrityError as e:
            os.remove(file_path)
            error_msg = str(e.orig)
            raise HTTPException(status_code=400, detail=f"Error uploading photo: {error_msg}")
    
    async def get_all_photos(self, session: AsyncSession):
        return await self.repository.get_all(session)
    
    async def get_photo_by_id(self, photo_id: int, session: AsyncSession):
        photo = await self.repository.get_by_id(photo_id, session)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        return photo

    async def get_photo_by_grade(self, grade: int, session: AsyncSession):
        photo = await self.repository.get_by_grade(grade, session)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        return photo

    async def get_photo_by_parallel(self, parallel: str, session: AsyncSession):
        photo = await self.repository.get_by_parallel(parallel, session)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        return photo

    async def update_photo(self, photo_id: int, photo_data: schemas.PhotoUpdateRequest, session: AsyncSession):
        update_data = {"date": photo_data.date, "description": photo_data.description, "grade": photo_data.grade, "parallel": photo_data.parallel, "updated_at": datetime.now(timezone.utc)}
        updated_photo = await self.repository.update(photo_id, update_data, session)
        if not updated_photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        return {"message": "Photo updated successfully"}

    async def delete_photo(self, photo_id: int, path: str, session: AsyncSession):
        result = await self.repository.delete(photo_id, session)
        if result["message"] == "Photo not found":
            raise HTTPException(status_code=404, detail="Photo not found")
        os.remove(path)
        return result
