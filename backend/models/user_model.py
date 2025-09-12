import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Boolean, Float, Enum as SQLEnum
from database import Base

class UserRoles(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hashed = Column(String, nullable=False)
    role = Column(SQLEnum(UserRoles), nullable=False)
    is_active = Column(Boolean, nullable=False)

    vk_id = Column(String, nullable=True, unique=True)
    yandex_id = Column(String, nullable=True, unique=True)
    google_id = Column(String, nullable=True, unique=True)
    oauth_provider = Column(String, nullable=True)  # 'vk', 'yandex', 'google', 'local'
    avatar_url = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    
    def __repr__(self):
        return f"User(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}')"
    