import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
ENVIRONMENT = os.getenv("ENVIRONMENT")

if ENVIRONMENT == "local":
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Supabase u otros servicios externos requieren SSL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

engine = create_engine(DATABASE_URL, pool_size=2, max_overflow=3)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🔍 Prueba de conexión opcional
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()"))
            print("✅ Conexión exitosa:", result.scalar())
    except Exception as e:
        print("❌ Error al conectar:", e)
