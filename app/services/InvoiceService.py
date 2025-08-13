from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from app.database.database import SessionLocal
from app.database.models import User, Invoice, InvoiceItem, LegalCase, Client, Account
from app.database.enums import InvoiceStatusEnum
from app.schemas.createInvoiceRequest import CreateInvoiceRequest
from app.schemas.invoiceResponse import InvoiceResponse, InvoiceItemResponse
from app.schemas.InvoiceSummaryResponse import InvoiceSummaryResponse, InvoiceSummaryItem, InvoiceItemDetail
from app.schemas.ClientSummaryResponse import ClientSummaryResponse, ClientSummaryItem
from app.schemas.InvoiceUpdateResponse import InvoiceUpdateRequest, InvoiceUpdateResponse
from datetime import date



class InvoiceService:

    @staticmethod
    def get_preview_invoice(invoice_id: int, user: User) -> InvoiceResponse | None:
        with SessionLocal() as session:
            invoice = (
                session.query(Invoice)
                .options(joinedload(Invoice.items), joinedload(Invoice.client))
                .filter(Invoice.id == invoice_id, Invoice.issued_by_user_id == user.id)
                .first()
            )

            if not invoice:
                return None

            legal_case = (
                session.query(LegalCase)
                .filter_by(client_id=invoice.client_id)
                .order_by(LegalCase.id.desc())
                .first()
            )

            # Status traducido
            status_map = {
                InvoiceStatusEnum.DUE: "Pendiente",
                InvoiceStatusEnum.PAYED: "Pagada",
                InvoiceStatusEnum.OVERDUE: "Vencida"
            }

            return InvoiceResponse(
                id=invoice.id,
                client=f"{invoice.client.first_name} {invoice.client.last_name}",
                case_number=str(legal_case.case_number) if legal_case and legal_case.case_number else "N/A",
                amount=sum(item.hours_worked * item.hourly_rate for item in invoice.items),
                issue_date=invoice.emission_date.strftime("%Y-%m-%d"),
                due_date=invoice.due_date.strftime("%Y-%m-%d"),
                status=status_map.get(invoice.status, "Pendiente"),
                items=[
                    InvoiceItemResponse(
                        name=item.description,
                        hours=item.hours_worked,
                        rate=item.hourly_rate
                    )
                    for item in invoice.items
                ]
            )
            
    @staticmethod
    def create_preview_invoice(payload: CreateInvoiceRequest, user: User) -> InvoiceResponse:
        with SessionLocal() as session:
            current_year = date.today().year
            last_invoice = (
                session.query(Invoice)
                .filter(Invoice.emission_date.between(f"{current_year}-01-01", f"{current_year}-12-31"))
                .order_by(Invoice.invoice_number.desc())
                .first()
            )
            next_invoice_number = (last_invoice.invoice_number + 1) if last_invoice else 1000

            invoice = Invoice(
                invoice_number=next_invoice_number,
                client_id=payload.client_id,
                emission_date=payload.emission_date,
                due_date=payload.due_date,
                issued_by_user_id=user.id,
                status=InvoiceStatusEnum.DUE
            )
            session.add(invoice)
            session.flush()

            total = 0
            items = []

            for item in payload.items:
                amount = item.hours_worked * item.hourly_rate
                total += amount

                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item.description,
                    hours_worked=item.hours_worked,
                    hourly_rate=item.hourly_rate
                )
                session.add(invoice_item)
                items.append(invoice_item)

            client = session.query(Client).filter(Client.id == invoice.client_id).first()
            legal_case = (
                session.query(LegalCase)
                .filter_by(client_id=invoice.client_id)
                .order_by(LegalCase.id.desc())
                .first()
            )

            session.commit()
            session.refresh(invoice)

            # Status traducido
            status_map = {
                InvoiceStatusEnum.DUE: "Pendiente",
                InvoiceStatusEnum.PAYED: "Pagada",
                InvoiceStatusEnum.OVERDUE: "Vencida"
            }

            return InvoiceResponse(
                id=invoice.id,
                client=f"{client.first_name} {client.last_name}" if client else "N/A",
                case_number=str(legal_case.case_number) if legal_case and legal_case.case_number else "N/A",
                issue_date=invoice.emission_date.strftime("%Y-%m-%d"),
                due_date=invoice.due_date.strftime("%Y-%m-%d"),
                status=status_map.get(invoice.status, "Pendiente"),
                amount=total,
                items=[
                    InvoiceItemResponse(
                        name=item.description,
                        hours=item.hours_worked,
                        rate=item.hourly_rate
                    )
                    for item in items
                ]
            )
            
    @staticmethod
    def update_invoice_status(payload: InvoiceUpdateRequest, user: User) -> InvoiceUpdateResponse:
        with SessionLocal() as session:
            invoice = session.query(Invoice).filter(Invoice.id == payload.id).first()

            if not invoice:
                raise HTTPException(status_code=404, detail="Factura no encontrada")

            invoice.status = payload.status
            session.commit()
            session.refresh(invoice)

            return InvoiceUpdateResponse(
                id=invoice.id,
                status=invoice.status,
                message="Estado de factura actualizado correctamente"
            )
            
    @staticmethod
    def delete_invoice(invoice_id: int, user):
        session = SessionLocal()

        invoice = session.query(Invoice).filter_by(id=invoice_id, issued_by_user_id=user.id).first()

        if not invoice:
            session.close()
            return False

        session.delete(invoice)
        session.commit()
        session.close()
        return True

    @staticmethod
    def get_all_invoices(user: User) -> InvoiceSummaryResponse:
        with SessionLocal() as session:
            invoices = (
                session.query(Invoice)
                .options(joinedload(Invoice.client), joinedload(Invoice.items))
                .filter(Invoice.issued_by_user_id == user.id)
                .order_by(Invoice.emission_date.desc())
                .all()
            )

            # Status traducido
            status_map = {
                InvoiceStatusEnum.DUE: "Pendiente",
                InvoiceStatusEnum.PAYED: "Pagada",
                InvoiceStatusEnum.OVERDUE: "Vencida"
            }

            invoice_summaries = []
            for invoice in invoices:
                # Obtener el caso más reciente del cliente (lógica temporal)
                legal_case = (
                    session.query(LegalCase)
                    .filter_by(client_id=invoice.client_id)
                    .order_by(LegalCase.id.desc())
                    .first()
                )

                # Procesar items de la factura
                items_detail = []
                total_amount = 0
                
                for item in invoice.items:
                    item_total = item.hours_worked * item.hourly_rate
                    total_amount += item_total
                    
                    items_detail.append(InvoiceItemDetail(
                        description=item.description,
                        hours_worked=item.hours_worked,
                        hourly_rate=item.hourly_rate,
                        item_total=item_total
                    ))
                
                invoice_summaries.append(InvoiceSummaryItem(
                    id=invoice.id,
                    invoice_number=invoice.invoice_number,
                    client_name=f"{invoice.client.first_name} {invoice.client.last_name}",
                    case_number=str(legal_case.case_number) if legal_case and legal_case.case_number else "N/A",
                    emission_date=invoice.emission_date.strftime("%Y-%m-%d"),
                    due_date=invoice.due_date.strftime("%Y-%m-%d"),
                    status=status_map.get(invoice.status, "Pendiente"),
                    total_amount=total_amount,
                    items=items_detail
                ))

            return InvoiceSummaryResponse(
                invoices=invoice_summaries,
                total_count=len(invoice_summaries)
            )

    @staticmethod
    def get_clients_for_invoice(user: User) -> ClientSummaryResponse:
        with SessionLocal() as session:
            # Obtener todos los clientes asociados a la cuenta del usuario
            clients = (
                session.query(Client)
                .join(Account.clients)
                .filter(Account.id == user.account_id)
                .order_by(Client.first_name, Client.last_name)
                .all()
            )

            client_summaries = []
            for client in clients:
                client_summaries.append(ClientSummaryItem(
                    id=client.id,
                    first_name=client.first_name,
                    last_name=client.last_name,
                    email=client.email,
                    phone_1=client.phone_1 if client.phone_1 else "",
                    dni=client.dni
                ))

            return ClientSummaryResponse(
                clients=client_summaries,
                total_count=len(client_summaries)
            )