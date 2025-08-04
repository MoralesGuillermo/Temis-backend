# In-built dependencies
from typing import Union
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import (auth_router, legal_case_router, invoice_router, notification_router)

load_dotenv()

# Origins for CORS
origins = [
    "http://localhost:3000",
    "http://ec2-78-13-106-228.mx-central-1.compute.amazonaws.com:3000"
    "https://ec2-78-13-106-228.mx-central-1.compute.amazonaws.com:3000",
    "http://78.13.106.228:3000",
    "https://78.13.106.228:3000"
    ]

environment = os.getenv("ENVIRONMENT")
if environment == "production":
    app = FastAPI(docs_url=None, redoc_url=None)
else:
    app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Esto debería ordenarse en orden alfabetico o cómo?
app.include_router(auth_router.router)
app.include_router(legal_case_router.router)
app.include_router(invoice_router.router)
app.include_router(notification_router.router)



