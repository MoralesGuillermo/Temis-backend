from app.database.database import SessionLocal
from app.database.models import User, LegalCase
from app.schemas.invoicePreviewResponse import InvoicePreviewResponse, InvoiceItemPreview
from app.database.enums import InvoiceStatusEnum
from sqlalchemy import text

class InvoiceService:
    # Supongamos que utiliza los modelos, SUPONGAMOS
    @staticmethod
    def get_preview_invoice(invoice_id: int, user: User) -> InvoicePreviewResponse | None:
        with SessionLocal() as session:
            # Obtener datos de la factura y cliente
            result = session.execute(text("""
                SELECT i.id, i.invoice_number, i.client_id, i.emission_date, i.due_date,
                       i.issued_by_user_id, i.status,
                       c.first_name, c.last_name
                FROM invoice i
                JOIN client c ON i.client_id = c.id
                WHERE i.id = :invoice_id AND i.issued_by_user_id = :user_id
            """), {"invoice_id": invoice_id, "user_id": user.id}).fetchone()

            if not result:
                return None

            invoice_id, invoice_number, client_id, emission_date, due_date, _, status, first_name, last_name = result

            # Obtener último caso legal
            legal_case = (
                session.query(LegalCase)
                .filter_by(client_id=client_id)
                .order_by(LegalCase.id.desc())
                .first()
            )

            # Obtener ítems de la factura
            items = session.execute(text("""
                SELECT description, hours_worked, hourly_rate
                FROM invoice_item
                WHERE invoice_id = :invoice_id
            """), {"invoice_id": invoice_id}).fetchall()

            # Calcular monto total
            total_amount = sum(item.hours_worked * item.hourly_rate for item in items)

            # Construir respuesta
            return InvoicePreviewResponse(
                id=invoice_id,
                client=f"{first_name} {last_name}",
                caseNumber=legal_case.case_number if legal_case and legal_case.case_number else "N/A",
                amount=total_amount,
                issueDate=emission_date.strftime("%Y-%m-%d"),
                dueDate=due_date.strftime("%Y-%m-%d"),
                status=InvoiceStatusEnum(status).name,
                items=[
                    InvoiceItemPreview(
                        name=item.description,
                        hours=item.hours_worked,
                        rate=item.hourly_rate
                    )
                    for item in items
                ]
            )