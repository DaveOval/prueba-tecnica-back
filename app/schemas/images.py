from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
        from_attributes = True

class ImageResponse(ImageInDB):
    pass 