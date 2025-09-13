from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Boolean, Float
from database import Base

class Photo(Base):
    __tablename__ = 'photos'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    path = Column(String, nullable=False)

    description = Column(String, nullable=True)
    grade = Column(Integer, nullable=True)
    parallel = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
