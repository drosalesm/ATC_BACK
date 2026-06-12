from pydantic import BaseModel, EmailStr
from typing import Optional


# ──────────────────────────────────────────────
# CREATE — solo nombre obligatorio
# ──────────────────────────────────────────────
class CompanyCreate(BaseModel):
    nombre: str

    razon_social: Optional[str] = None
    ruc: Optional[str] = None
    lema: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    maps_url: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    horario_atencion: Optional[str] = None


# ──────────────────────────────────────────────
# UPDATE — todos opcionales
# ──────────────────────────────────────────────
class CompanyUpdate(BaseModel):
    nombre: Optional[str] = None
    razon_social: Optional[str] = None
    ruc: Optional[str] = None
    lema: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    maps_url: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    horario_atencion: Optional[str] = None


# ──────────────────────────────────────────────
# RESPONSE — incluye id y rutas de archivos
# ──────────────────────────────────────────────
class CompanyResponse(BaseModel):
    id: int
    nombre: str
    razon_social: Optional[str] = None
    ruc: Optional[str] = None
    lema: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    maps_url: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    horario_atencion: Optional[str] = None
    logo_path: Optional[str] = None
    favicon_path: Optional[str] = None

    class Config:
        from_attributes = True