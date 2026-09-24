from fastapi import FastAPI
from .database import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime
from sqlalchemy.sql import func

class User(Base):
    __tablename__='users'

    id = Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,nullable=False)
    username=Column(String,unique=True,nullable=False)
    first_name=Column(String,nullable=False)
    last_name=Column(String,nullable=False)
    hashed_password=Column(String,nullable=False)
    is_active=Column(Boolean,default=True)
    role=Column(String)

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    # Standard strings with hardcoded default values
    status = Column(String, default="todo", nullable=False)
    priority = Column(String, default="medium", nullable=False)
    due_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer,ForeignKey("users.id"))
