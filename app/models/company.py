from app.db.database import Base
from sqlalchemy import Column, Integer, String


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)

    # Identidad
    nombre = Column(String(200), nullable=False)
    razon_social = Column(String(200), nullable=True)
    ruc = Column(String(50), nullable=True)
    lema = Column(String(300), nullable=True)

    # Contacto
    correo = Column(String(150), nullable=True)
    telefono = Column(String(30), nullable=True)
    whatsapp = Column(String(30), nullable=True)

    # Ubicación
    direccion = Column(String(300), nullable=True)
    ciudad = Column(String(100), nullable=True)
    maps_url = Column(String(500), nullable=True)

    # Web
    website = Column(String(200), nullable=True)

    # Redes sociales
    facebook = Column(String(200), nullable=True)
    instagram = Column(String(200), nullable=True)
    linkedin = Column(String(200), nullable=True)
    twitter = Column(String(200), nullable=True)
    youtube = Column(String(200), nullable=True)
    tiktok = Column(String(200), nullable=True)

    # Operación
    horario_atencion = Column(String(200), nullable=True)

    # Identidad visual
    logo_path = Column(String(500), nullable=True)
    favicon_path = Column(String(500), nullable=True)