from app.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String,Float,ForeignKey,Boolean



class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    sku = Column(String(50), unique=True, nullable=False)  # Código único
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

    # Para la imagen:
    image_path = Column(String(500), nullable=True)   # Ruta donde se guardó
    image_filename = Column(String(200), nullable=True)  # Nombre del archivo
    features = Column(String(2000), nullable=True)   # Productos: características | Servicios: qué incluye
    specs    = Column(String(2000), nullable=True)   # Productos: especificaciones técnicas | Servicios: no se usa


    # Llave foránea
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Relación
    category = relationship("Category", back_populates="products")



class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # "Servidores", "Laptops", etc.
    description = Column(String(255))
    tipo = Column(String(50), nullable=False)  # "infraestructura" o "desarrollo"
    active = Column(Boolean, default=True)
    
    # Relación
    products = relationship("Product", back_populates="category")