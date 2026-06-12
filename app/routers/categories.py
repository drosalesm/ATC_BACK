from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.products import Category
from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse
from app.utils.utils import format_response
from app.auth.auth import get_current_user
from app.models.users import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva categoría"""
    try:
        # Verificar si ya existe una categoría con el mismo nombre
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            return format_response(400, "Ya existe una categoría con ese nombre")
        
        # Crear nueva categoría
        new_category = Category(
            name=category.name,
            description=category.description,
            tipo=category.tipo,
            active=category.active
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        # Datos de respuesta
        category_data = {
            "id": new_category.id,
            "name": new_category.name,
            "description": new_category.description,
            "tipo": new_category.tipo,
            "active": new_category.active
        }
        
        return format_response(201, "Categoría creada exitosamente", category_data)
    
    except Exception as e:
        print(f"Error al crear categoría: {e}")
        return format_response(500, "Error interno del servidor")


@router.get("/")
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tipo: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Listar todas las categorías con filtros opcionales"""
    try:
        query = db.query(Category)
        
        # Aplicar filtros
        if tipo:
            query = query.filter(Category.tipo == tipo)
        if active is not None:
            query = query.filter(Category.active == active)
        
        # Paginación
        categories = query.offset(skip).limit(limit).all()
        
        if not categories:
            return format_response(404, "No se encontraron categorías")
        
        # Serializar datos
        categories_list = [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "tipo": cat.tipo,
                "active": cat.active,
                "products_count": len(cat.products)  # Cantidad de productos en esta categoría
            }
            for cat in categories
        ]
        
        return format_response(200, "Categorías obtenidas exitosamente", categories_list)
    
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return format_response(500, "Error interno del servidor")


@router.get("/{category_id}")
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener una categoría específica por ID"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return format_response(404, "Categoría no encontrada")
        
        # Datos de la categoría
        category_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "tipo": category.tipo,
            "active": category.active,
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "price": p.price,
                    "stock": p.stock
                }
                for p in category.products[:10]  # Límite de 10 productos por respuesta
            ]
        }
        
        return format_response(200, "Categoría obtenida exitosamente", category_data)
    
    except Exception as e:
        print(f"Error al obtener categoría: {e}")
        return format_response(500, "Error interno del servidor")


@router.put("/{category_id}")
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar una categoría existente"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return format_response(404, "Categoría no encontrada")
        
        # Verificar si el nuevo nombre ya existe (si se está cambiando el nombre)
        if category_update.name and category_update.name != category.name:
            existing = db.query(Category).filter(Category.name == category_update.name).first()
            if existing:
                return format_response(400, "Ya existe otra categoría con ese nombre")
        
        # Actualizar solo los campos proporcionados
        if category_update.name is not None:
            category.name = category_update.name
        if category_update.description is not None:
            category.description = category_update.description
        if category_update.tipo is not None:
            category.tipo = category_update.tipo
        if category_update.active is not None:
            category.active = category_update.active
        
        db.commit()
        db.refresh(category)
        
        # Datos actualizados
        updated_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "tipo": category.tipo,
            "active": category.active
        }
        
        return format_response(200, "Categoría actualizada exitosamente", updated_data)
    
    except Exception as e:
        print(f"Error al actualizar categoría: {e}")
        return format_response(500, "Error interno del servidor")


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar una categoría (solo si no tiene productos asociados)"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return format_response(404, "Categoría no encontrada")
        
        # Verificar si tiene productos asociados
        if category.products:
            return format_response(
                400, 
                f"No se puede eliminar la categoría porque tiene {len(category.products)} productos asociados. Primero elimina o reasigna los productos."
            )
        
        # Eliminar categoría
        db.delete(category)
        db.commit()
        
        return format_response(200, "Categoría eliminada exitosamente")
    
    except Exception as e:
        print(f"Error al eliminar categoría: {e}")
        return format_response(500, "Error interno del servidor")


@router.patch("/{category_id}/toggle-status")
def toggle_category_status(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activar o desactivar una categoría (soft delete)"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        
        if not category:
            return format_response(404, "Categoría no encontrada")
        
        # Cambiar el estado
        category.active = not category.active
        db.commit()
        db.refresh(category)
        
        status_text = "activada" if category.active else "desactivada"
        
        return format_response(
            200, 
            f"Categoría {status_text} exitosamente",
            {
                "id": category.id,
                "name": category.name,
                "active": category.active
            }
        )
    
    except Exception as e:
        print(f"Error al cambiar estado de categoría: {e}")
        return format_response(500, "Error interno del servidor")