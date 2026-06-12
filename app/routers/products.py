from fastapi import APIRouter, Depends, File, UploadFile, Form, Query

from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.products import Product
from app.models.products import Category
from app.schemas.products import ProductCreate, ProductUpdate, ProductResponse

from pathlib import Path
import shutil
import uuid
import os
from app.utils.utils import format_response
from app.auth.auth import get_current_user
from app.models.users import User

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = Path("static/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


# ──────────────────────────────────────────────
# POST /products  →  Crear producto (sin imagen)
# ──────────────────────────────────────────────
@router.post("/")
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo producto (JSON puro, sin imagen)"""
    try:
        # 1. Verificar SKU único
        existing_sku = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_sku:
            return format_response(400, f"Ya existe un producto con el SKU '{product.sku}'")

        # 2. Verificar que la categoría existe
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            return format_response(404, "La categoría especificada no existe")

        if not category.active:
            return format_response(400, "No se pueden crear productos en una categoría inactiva")

        # 3. Crear producto
        new_product = Product(
            name=product.name,
            description=product.description,
            sku=product.sku,
            price=product.price,
            stock=product.stock,
            category_id=product.category_id,
            image_path=None,
            features=product.features,
            specs=product.specs
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        product_data = {
            "id": new_product.id,
            "name": new_product.name,
            "description": new_product.description,
            "sku": new_product.sku,
            "price": new_product.price,
            "stock": new_product.stock,
            "category_id": new_product.category_id,
            "category_name": category.name,
            "image_path": None
        }

        return format_response(201, "Producto creado exitosamente", product_data)

    except Exception as e:
        print(f"Error al crear producto: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# POST /products/{id}/image  →  Subir imagen
# ──────────────────────────────────────────────
@router.post("/{product_id}/image")
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Subir o reemplazar la imagen de un producto existente.
    - Si el producto no existe → 404
    - Si la extensión no es válida → 400
    - Si ya tenía imagen → se elimina la anterior y se reemplaza
    """
    try:
        # 1. Verificar que el producto existe
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return format_response(404, "Producto no encontrado")

        # 2. Validar extensión del archivo
        file_extension = Path(image.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return format_response(
                400,
                f"Formato de imagen no válido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 3. Si ya tiene imagen, eliminar el archivo anterior del disco
        if product.image_path:
            old_file = Path(product.image_path)
            if old_file.exists():
                os.remove(old_file)

        # 4. Guardar nueva imagen con nombre único
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_location = UPLOAD_DIR / unique_filename

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # 5. Actualizar ruta en la BD
        product.image_path = f"static/products/{unique_filename}"
        product.image_filename = image.filename

        db.commit()
        db.refresh(product)

        image_data = {
            "id": product.id,
            "name": product.name,
            "image_path": product.image_path,
            "image_filename": product.image_filename
        }

        return format_response(200, "Imagen subida exitosamente", image_data)

    except Exception as e:
        print(f"Error al subir imagen: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# GET /products
# ──────────────────────────────────────────────
@router.get("/")
def get_products(
    db: Session = Depends(get_db),
    category_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    search: Optional[str] = Query(None, description="Buscar por nombre o SKU"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo"),
    min_stock: Optional[int] = Query(None, description="Stock mínimo"),
    low_stock: Optional[bool] = Query(None, description="Productos con stock bajo (menor a 5)"),
    skip: int = Query(0, description="Número de registros a saltar"),
    limit: int = Query(100, description="Límite de registros")
):
    """Listar productos con filtros opcionales"""
    try:
        query = db.query(Product)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if search:
            query = query.filter(
                (Product.name.ilike(f"%{search}%")) |
                (Product.sku.ilike(f"%{search}%"))
            )

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        if min_stock is not None:
            query = query.filter(Product.stock >= min_stock)

        if low_stock:
            query = query.filter(Product.stock < 5)

        products = query.offset(skip).limit(limit).all()

        if not products:
            return format_response(404, "No se encontraron productos")

        products_list = []
        for p in products:
            category = db.query(Category).filter(Category.id == p.category_id).first()
            products_list.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "sku": p.sku,
                "price": p.price,
                "stock": p.stock,
                "category_id": p.category_id,
                "category_name": category.name if category else "Sin categoría",
                "category_tipo": category.tipo if category else None,
                "image_path": p.image_path,
                "features": p.features,
                "specs": p.specs
            })

        return format_response(200, "Productos obtenidos exitosamente", products_list)

    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# GET /products/{product_id}
# ──────────────────────────────────────────────
@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Obtener un producto específico por ID"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return format_response(404, "Producto no encontrado")

        category = db.query(Category).filter(Category.id == product.category_id).first()

        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "sku": product.sku,
            "price": product.price,
            "stock": product.stock,
            "category_id": product.category_id,
            "category_name": category.name if category else "Sin categoría",
            "category_tipo": category.tipo if category else None,
            "category_active": category.active if category else None,
            "image_path": product.image_path,
            "features": product.features,
            "specs": product.specs  
        }

        return format_response(200, "Producto obtenido exitosamente", product_data)

    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# PUT /products/{product_id}
# ──────────────────────────────────────────────
@router.put("/{product_id}")
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar un producto existente"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        print(f"Producto encontrado para actualización: {product}")


        if not product:
            return format_response(404, "Producto no encontrado")

        if product_update.sku and product_update.sku != product.sku:
            existing_sku = db.query(Product).filter(Product.sku == product_update.sku).first()
            if existing_sku:
                return format_response(400, f"Ya existe otro producto con el SKU '{product_update.sku}'")

        if product_update.category_id:
            category = db.query(Category).filter(Category.id == product_update.category_id).first()
            if not category:
                return format_response(404, "La categoría especificada no existe")
            if not category.active:
                return format_response(400, "No se pueden asignar productos a una categoría inactiva")

        if product_update.name is not None:
            product.name = product_update.name
        if product_update.description is not None:
            product.description = product_update.description
        if product_update.sku is not None:
            product.sku = product_update.sku
        if product_update.price is not None:
            product.price = product_update.price
        if product_update.stock is not None:
            product.stock = product_update.stock
        if product_update.category_id is not None:
            product.category_id = product_update.category_id
        if product_update.features is not None:
            product.features = product_update.features
        if product_update.specs is not None:
            product.specs = product_update.specs


        db.commit()
        db.refresh(product)

        category = db.query(Category).filter(Category.id == product.category_id).first()

        updated_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "sku": product.sku,
            "price": product.price,
            "stock": product.stock,
            "category_id": product.category_id,
            "category_name": category.name if category else "Sin categoría",
            "image_path": product.image_path,
            "features": product.features,
            "specs": product.specs
        }

        return format_response(200, "Producto actualizado exitosamente", updated_data)

    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# DELETE /products/{product_id}
# ──────────────────────────────────────────────
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar un producto (y su imagen del disco si existe)"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return format_response(404, "Producto no encontrado")

        # Eliminar imagen del disco si existe
        if product.image_path:
            old_file = Path(product.image_path)
            if old_file.exists():
                os.remove(old_file)

        db.delete(product)
        db.commit()

        return format_response(200, "Producto eliminado exitosamente")

    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# DELETE /products/{product_id}/image
# ──────────────────────────────────────────────
@router.delete("/{product_id}/image")
def delete_product_image(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar solo la imagen de un producto sin eliminar el producto"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return format_response(404, "Producto no encontrado")

        if not product.image_path:
            return format_response(404, "El producto no tiene imagen asignada")

        # Eliminar archivo del disco
        old_file = Path(product.image_path)
        if old_file.exists():
            os.remove(old_file)

        # Limpiar referencia en BD
        product.image_path = None
        product.image_filename = None
        db.commit()

        return format_response(200, "Imagen eliminada exitosamente")

    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# PATCH /products/{product_id}/stock
# ──────────────────────────────────────────────
@router.patch("/{product_id}/stock")
def update_stock(
    product_id: int,
    quantity: int = Query(..., description="Cantidad a agregar (positivo) o quitar (negativo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar el stock de un producto (sumar o restar)"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return format_response(404, "Producto no encontrado")

        new_stock = product.stock + quantity

        if new_stock < 0:
            return format_response(400, f"Stock insuficiente. Stock actual: {product.stock}")

        previous_stock = product.stock
        product.stock = new_stock
        db.commit()
        db.refresh(product)

        stock_data = {
            "id": product.id,
            "name": product.name,
            "previous_stock": previous_stock,
            "current_stock": product.stock,
            "change": quantity
        }

        action = "agregado" if quantity > 0 else "retirado"
        return format_response(200, f"Stock actualizado: se ha {action} {abs(quantity)} unidades", stock_data)

    except Exception as e:
        print(f"Error al actualizar stock: {e}")
        return format_response(500, "Error interno del servidor")


# ──────────────────────────────────────────────
# GET /products/low-stock/summary
# ──────────────────────────────────────────────
@router.get("/low-stock/summary")
def get_low_stock_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resumen de productos con stock bajo (menor a 5 unidades)"""
    try:
        low_stock_products = db.query(Product).filter(Product.stock < 5).all()

        if not low_stock_products:
            return format_response(200, "No hay productos con stock bajo", [])

        summary = []
        for p in low_stock_products:
            category = db.query(Category).filter(Category.id == p.category_id).first()
            summary.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "stock": p.stock,
                "category_name": category.name if category else "Sin categoría",
                "alert": "CRÍTICO" if p.stock == 0 else "BAJO"
            })

        return format_response(200, f"Se encontraron {len(low_stock_products)} productos con stock bajo", summary)

    except Exception as e:
        print(f"Error al obtener resumen de stock bajo: {e}")
        return format_response(500, "Error interno del servidor")