import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Localizar el archivo .env (subiendo un nivel desde la carpeta actual 'API')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

# 2. Cargar las variables de entorno
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

# Validación de seguridad: Si no hay URL, el sistema se detiene con un error claro
if not DATABASE_URL:
    raise ValueError("ERROR: No se encontró la variable DATABASE_URL en el archivo .env. Verifica la ruta.")

# Configuración del motor de SQLAlchemy con pool settings para Supabase
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verifica conexiones antes de usarlas
    pool_recycle=3600       # Recicla conexiones cada hora (3600 segundos)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()