from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Boolean, Float
from database import Base

class Photo(Base):
    __tablename__ = 'photos'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    grade = Column(Integer, nullable=False)
    parallel = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
