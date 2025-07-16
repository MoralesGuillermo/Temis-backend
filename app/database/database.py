import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")  
DB_NAME = os.environ.get("DB_NAME")
ENVIRONMENT = os.environ.get("ENVIRONMENT")

if ENVIRONMENT == 'local':
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
else:
    # conexión en Supabase requiere SSL
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?sslmode=require'

engine = create_engine(DATABASE_URL, pool_size=2, max_overflow=3)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
