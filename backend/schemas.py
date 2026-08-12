
from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    marker_id: Optional[int] = None
    title: str
    author: str
    available: bool = True

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    marker_id: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    available: Optional[bool] = None

class BookOut(BookBase):
    id: int
    class Config:
        orm_mode = True
