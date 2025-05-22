from typing import List, Optional
from mongoengine import Document, StringField, ListField, DateTimeField
from pydantic import BaseModel
from datetime import datetime

class Image(Document):
    user_id = StringField(required=True)
    original_filename = StringField(required=True)
    original_path = StringField(required=True)
    processed_path = StringField(required=True)
    filter_name = StringField(default=None)
    filter_value = StringField(default=None)
    transformations = ListField(StringField(), default=list)  # Keep for backward compatibility
    uploaded_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Settings:
        name = "images"

    def get_filter_name(self):
        if self.filter_name is not None:
            return self.filter_name
        if self.transformations and len(self.transformations) > 0:
            return self.transformations[0]
        return None

    def get_filter_value(self):
        if self.filter_value is not None:
            return self.filter_value
        if self.transformations and len(self.transformations) > 1:
            return self.transformations[1]
        return None

class ImageBase(BaseModel):
    original_filename: str
    original_path: str
    processed_path: str
    filter_name: Optional[str] = None
    filter_value: Optional[str] = None

class ImageCreate(ImageBase):
    user_id: str

class ImageUpdate(BaseModel):
    processed_path: Optional[str] = None
    filter_name: Optional[str] = None
    filter_value: Optional[str] = None

class ImageInDB(ImageBase):
    id: str
    user_id: str
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True