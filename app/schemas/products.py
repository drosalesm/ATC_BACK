from pydantic import BaseModel
from typing import Optional


# ──────────────────────────────────────────────
# Base con campos comunes
# ──────────────────────────────────────────────
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    stock: int = 0
    category_id: int
    features: Optional[str] = None
    specs: Optional[str] = None

# ──────────────────────────────────────────────
# CREATE — JSON puro, sin imagen
# ──────────────────────────────────────────────
class ProductCreate(ProductBase):
    pass


# ──────────────────────────────────────────────
# UPDATE — todos los campos opcionales, sin imagen
# ──────────────────────────────────────────────
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    features: Optional[str] = None
    specs: Optional[str] = None

# ──────────────────────────────────────────────
# RESPONSE — incluye datos de categoría e imagen
# ──────────────────────────────────────────────
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    stock: int
    category_id: int
    category_name: Optional[str] = None
    image_path: Optional[str] = None      # Ruta del archivo en disco
    image_filename: Optional[str] = None  # Nombre original del archivo subido

    class Config:
        from_attributes = True  # Para SQLAlchemy (antes orm_mode)