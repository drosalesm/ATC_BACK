from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
import os

from app.db.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.utils.utils import format_response
from app.auth.auth import get_current_user
from app.models.users import User

router = APIRouter(prefix="/company", tags=["Company"])

UPLOAD_DIR = Path("static/company")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico", ".svg"}


# ──────────────────────────────────────────────
# GET /company  →  Obtener datos de la empresa
# ──────────────────────────────────────────────
@router.get("/")
def get_company(db: Session = Depends(get_db)):
    """Obtener la información de la empresa (público, no requiere auth)"""
    try:
        company = db.query(Company).first()

        if not company:
            return format_response(404, "No hay información de la empresa registrada")

        return format_response(200, "Información de la empresa obtenida exitosamente", {
            "id": company.id,
            "nombre": company.nombre,
            "razon_social": company.razon_social,
            "ruc": company.ruc,
            "lema": company.lema,
            "correo": company.correo,
            "telefono": company.telefono,
            "whatsapp": company.whatsapp,
            "direccion": company.direccion,
            "ciudad": company.ciudad,
            "maps_url": company.maps_url,
            "website": company.website,
            "facebook": company.facebook,
            "instagram": company.instagram,
            "linkedin": company.linkedin,
            "twitter": company.twitter,
            "youtube": company.youtube,
            "tiktok": company.tiktok,
            "horario_atencion": company.horario_atencion,
            "logo_path": company.logo_path,
            "favicon_path": company.favicon_path,
        })

    except Exception as e:
        print(f"Error al obtener información de la empresa: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# POST /company  →  Inicializar empresa (solo si no existe)
# ──────────────────────────────────────────────
@router.post("/")
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear el registro de la empresa — solo permitido si aún no existe"""
    try:
        existing = db.query(Company).first()
        if existing:
            return format_response(400, "Ya existe un registro de la empresa. Usa PUT para actualizar.")


        company = Company(**company_data.dict())


        db.add(company)
        db.commit()
        db.refresh(company)

        return format_response(201, "Información de la empresa creada exitosamente", {
            "id": company.id,
            "nombre": company.nombre
        })

    except Exception as e:
        print(f"Error al crear información de la empresa: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# PUT /company  →  Actualizar datos de la empresa
# ──────────────────────────────────────────────
@router.put("/")
def update_company(
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar la información de la empresa"""
    try:
        company = db.query(Company).first()

        if not company:
            return format_response(404, "No hay información de la empresa registrada. Usa POST para inicializar.")

        # Actualizar solo los campos enviados
        update_fields = company_data.dict(exclude_unset=True)

        for field, value in update_fields.items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)

        return format_response(200, "Información de la empresa actualizada exitosamente", {
            "id": company.id,
            "nombre": company.nombre
        })

    except Exception as e:
        print(f"Error al actualizar información de la empresa: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# POST /company/logo  →  Subir logo
# ──────────────────────────────────────────────
@router.post("/logo")
async def upload_logo(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Subir o reemplazar el logo de la empresa"""
    try:
        company = db.query(Company).first()
        if not company:
            return format_response(404, "No hay información de la empresa registrada. Usa POST para inicializar.")

        file_extension = Path(image.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return format_response(
                400,
                f"Formato no válido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Eliminar logo anterior si existe
        if company.logo_path:
            old_file = Path(company.logo_path)
            if old_file.exists():
                os.remove(old_file)

        unique_filename = f"logo_{uuid.uuid4().hex}{file_extension}"
        file_location = UPLOAD_DIR / unique_filename

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        company.logo_path = f"static/company/{unique_filename}"
        db.commit()

        return format_response(200, "Logo actualizado exitosamente", {
            "logo_path": company.logo_path
        })

    except Exception as e:
        print(f"Error al subir logo: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# POST /company/favicon  →  Subir favicon
# ──────────────────────────────────────────────
@router.post("/favicon")
async def upload_favicon(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Subir o reemplazar el favicon de la empresa"""
    try:
        company = db.query(Company).first()
        if not company:
            return format_response(404, "No hay información de la empresa registrada. Usa POST para inicializar.")

        file_extension = Path(image.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return format_response(
                400,
                f"Formato no válido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Eliminar favicon anterior si existe
        if company.favicon_path:
            old_file = Path(company.favicon_path)
            if old_file.exists():
                os.remove(old_file)

        unique_filename = f"favicon_{uuid.uuid4().hex}{file_extension}"
        file_location = UPLOAD_DIR / unique_filename

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        company.favicon_path = f"static/company/{unique_filename}"
        db.commit()

        return format_response(200, "Favicon actualizado exitosamente", {
            "favicon_path": company.favicon_path
        })

    except Exception as e:
        print(f"Error al subir favicon: {e}")
        return format_response(500, "Error interno del servidor")