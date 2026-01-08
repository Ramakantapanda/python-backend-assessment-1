from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    external_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExternalApiResponse(BaseModel):
    id: int
    title: str
    body: str
    userId: int


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None