from fastapi import APIRouter, Depends, status, HTTPException, Request
from app.schemas.createInvoiceRequest import CreateInvoiceRequest
from app.schemas.invoiceResponse import InvoiceResponse
from app.schemas.InvoiceUpdateResponse import InvoiceUpdateRequest, InvoiceUpdateResponse
from app.schemas.InvoiceSummaryResponse import InvoiceSummaryResponse
from app.services.InvoiceService import InvoiceService
from app.services.AuthService import AuthService

router = APIRouter(prefix="/invoice", tags=["invoice"])

@router.get("/preview", response_model=InvoiceResponse)
def preview_invoice(invoice_id: int, request: Request):
    jwt = request.cookies.get("accessToken") 
    user = AuthService.get_active_user(jwt)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    
    invoice = InvoiceService.get_preview_invoice(invoice_id, user)

    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada o sin acceso")

    return invoice

@router.post("/create-preview", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_preview_invoice(payload: CreateInvoiceRequest, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)

    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    invoice = InvoiceService.create_preview_invoice(payload, user)
    return invoice

@router.put("/status", response_model=InvoiceUpdateResponse)
def update_invoice_status(payload: InvoiceUpdateRequest, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)

    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    response = InvoiceService.update_invoice_status(payload, user)
    return response

@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_invoice(invoice_id: int, request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    deleted = InvoiceService.delete_invoice(invoice_id, user)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada o sin acceso")

    return {"message": "Factura eliminada correctamente"}



@router.get("/all", response_model=InvoiceSummaryResponse)
def get_all_invoices(request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    invoices = InvoiceService.get_all_invoices(user)
    return invoices