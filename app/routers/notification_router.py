from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.utils.email.EmailService import EmailService

router = APIRouter(prefix="/notifications", tags=["notifications"])

class InvoiceEmailRequest(BaseModel):
    to_email: EmailStr
    client_name: str
    invoice_id: int

@router.post("/invoice", status_code=status.HTTP_202_ACCEPTED)
async def send_invoice_email(payload: InvoiceEmailRequest):
    # Esta parte de `data` depende del contenido de la plantilla HTML
    data = {
        "name": payload.client_name,
        "invoice_id": payload.invoice_id,
        # Se puede agregar más si el HTML lo necesita
    }

    success = await EmailService.send_email(
        to_email=payload.to_email,
        subject=f"Factura #{payload.invoice_id} disponible",
        template_name="InvoiceTemplate.html",
        data=data
    )

    if not success:
        raise HTTPException(status_code=500, detail="No se pudo enviar el correo")
    
    return {"message": "Correo de factura enviado correctamente"}