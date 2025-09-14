from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi import File, UploadFile
from datetime import datetime
import re
from typing import Optional, List, Any, Dict
import enum

#Схемы юзера

class UserModel(BaseModel):
    """
    Модель пользователя для документации Swagger
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    email: str = Field(..., description="Электронная почта пользователя")
    password_hashed: str = Field(..., description="Хэшированный пароль пользователя")
    role: str = Field(..., description="Роль пользователя")
    is_active: bool = Field(..., description="Статус активности пользователя")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password_hashed": "Password123",
                "role": "admin",
                "is_active": True
            }
        }
    }

class UserCreateRequest(BaseModel):
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    email: str = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., description="Пароль пользователя")
    role: str = Field(..., description="Роль пользователя")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Invalid email format")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "Password123",
                "role": "admin"
            }
        }
    }

class UserCreateResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате операции")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "User created successfully"
            }
        }
    }


class UserUpdateRequest(BaseModel):
    id: int = Field(None, description="Уникальный идентификатор пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    email: str = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., description="Пароль пользователя")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError("Invalid email format")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "Password123"
            }
        }
    }

class UserUpdateResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате операции")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "User updated successfully"
            }
        }
    }


class UserReadRequest(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор пользователя")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1
            }
        }
    }

class UserReadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    email: str = Field(..., description="Электронная почта пользователя")
    password_hashed: str = Field(..., description="Хэшированный пароль пользователя")
    role: str = Field(..., description="Роль пользователя")
    is_active: bool = Field(..., description="Статус активности пользователя")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password_hashed": "$2b$12$omkbnYhVkqFulQiFv5GV3.dDmrTNtZwYa.qWIEyz.s.8owZcaEWL.",
                "role": "admin",
                "is_active": True
            }
        }
    }

class UserDeleteRequest(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1
            }
        }
    }
    
class UserDeleteResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате операции")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "User deleted successfully"
            }
        }
    }


#Схемы фото

class PhotoModel(BaseModel):
    """
    Модель фото для документации Swagger
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Уникальный идентификатор фото")
    date: datetime = Field(..., description="Дата фото")
    path: str = Field(..., description="Путь к фото")
    description: str = Field(..., description="Описание фото")
    grade: int = Field(..., description="Класс на фото")
    parallel: str = Field(..., description="Буква параллели класса на фото")
    created_at: datetime = Field(..., description="Дата создания фото")
    updated_at: datetime = Field(..., description="Дата обновления фото")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "date": "2025-09-09",
                "path": "/images/1010.jpg",
                "description": "Фото 10А класса",
                "grade": 10,
                "parallel": "A",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-23"
            }
        }
    }

class PhotoCreateRequest(BaseModel):
    file: UploadFile = File(..., description="Сам файл фото")
    date: datetime = Field(..., description="Дата фото")
    description: str = Field(..., description="Описание фото")
    grade: int = Field(..., description="Класс на фото")
    parallel: str = Field(..., description="Буква параллели класса на фото")

    @field_validator('grade')
    @classmethod
    def validate_grade(cls, v):
        if v is None:
            return v
        if not (v > 0 and v < 12):
            raise ValueError("Invalid grade")
        return v
    
    @field_validator('parallel')
    @classmethod
    def validate_parallel(cls, v):
        if v is None:
            return v
        if not (re.match(r'^[А-Я]$', v) and len(v) == 1):
            raise ValueError("Invalid parallel")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-09-09", 
                "description": "Фото 10А класса",
                "grade": 10,
                "parallel": "A"
            }
        }
    }

class PhotoCreateResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате операции")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Photo created successfully"
            }
        }
    }

class PhotoReadRequest(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор фото")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1
            }
        }
    }

class PhotoReadResponse(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор фото")
    date: datetime = Field(..., description="Дата фото")
    path: str = Field(..., description="Путь к фото")
    description: str = Field(..., description="Описание фото")
    grade: int = Field(..., description="Класс на фото")
    parallel: str = Field(..., description="Буква параллели класса на фото")
    created_at: datetime = Field(..., description="Дата создания фото")
    updated_at: datetime = Field(..., description="Дата обновления фото")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "date": "2025-09-09",
                "path": "/images/1010.jpg",
                "description": "Фото 10А класса",
                "grade": 10,
                "parallel": "A",
                "created_at": "2025-01-01",
                "updated_at": "2025-01-23"
            }
        }
    }

class PhotoUpdateRequest(BaseModel):
    date: datetime = Field(..., description="Дата фото")
    description: str = Field(..., description="Описание фото")
    grade: int = Field(..., description="Класс на фото")
    parallel: str = Field(..., description="Буква параллели класса на фото")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-09-09",
                "description": "Фото 10А класса",
                "grade": 10,
                "parallel": "A"
            }
        }
    }

class PhotoUpdateResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате операции")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Photo updated successfully"
            }
        }
    }

class PhotoDeleteRequest(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор фото")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1
            }
        }
    }
    
class PhotoDeleteResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате операции")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Photo deleted successfully"
            }
        }
    }

class ErrorResponse(BaseModel):
    """Модель для ответов с ошибками"""
    detail: str = Field(..., description="Детальное описание ошибки")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Resource not found"
            }
        }
    }

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str

class CSRFToken(BaseModel):
    csrf_token: str