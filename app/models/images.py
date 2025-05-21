from typing import List, Optional
from mongoengine import Document, StringField, ListField, DateTimeField
from pydantic import BaseModel
from datetime import datetime

class Image(Document):
    user_id = StringField(required=True)
    original_filename = StringField(required=True)
    original_path = StringField(required=True)
    processed_path = StringField(required=True)
    transformations = ListField(StringField(), default=list)
    uploaded_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Settings:
        name = "images"

class ImageBase(BaseModel):
    original_filename: str
    original_path: str
    processed_path: str
    transformations: List[str]

class ImageCreate(ImageBase):
    user_id: str

class ImageUpdate(BaseModel):
    processed_path: Optional[str] = None
    transformations: Optional[List[str]] = None

class ImageInDB(ImageBase):
    id: str
    user_id: str
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True