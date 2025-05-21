from typing import Optional
from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime

class User(Document):
    name = StringField(required=True)
    last_name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    is_active = BooleanField(default=True)
    role = StringField(required=True, default="user")
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)


class UserBase(BaseModel):
    name: str
    last_name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        
        
        
        