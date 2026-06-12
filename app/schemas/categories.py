from pydantic import BaseModel
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tipo: str  # "infraestructura" o "desarrollo"
    active: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tipo: Optional[str] = None
    active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    tipo: str
    active: bool