from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia esta URL con tus credenciales de PostgreSQL
DATABASE_URL = "postgresql://postgres:123@localhost:5432/atc_app"

# Crea el motor
engine = create_engine(DATABASE_URL)

# Crea la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependency para inyectar la DB en tus rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
