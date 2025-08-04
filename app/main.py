# In-built dependencies
from typing import Union

from fastapi import FastAPI

from app.routers import (auth_router, legal_case_router, invoice_router, notification_router)

app = FastAPI()
# TODO: Generate and add app's middleware


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



