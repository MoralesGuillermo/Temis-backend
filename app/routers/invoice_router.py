from fastapi import APIRouter, Request, HTTPException, status
from app.services.InvoiceService import InvoiceService
from app.services.AuthService import AuthService

router = APIRouter(prefix="/invoice", tags=["invoice"])

@router.get("/preview")
def preview_invoice(invoice_id: int, request: Request):
    jwt = request.cookies.get("accessToken") 
    user = AuthService.get_active_user(jwt)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    invoice = InvoiceService.get_preview_invoice(invoice_id, user)

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada o sin acceso")

    return invoice