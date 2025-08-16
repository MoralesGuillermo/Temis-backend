"""Dashboard service - centraliza lógica del dashboard"""
from sqlalchemy.orm import joinedload
from datetime import datetime, date  # ← ASEGURAR QUE ESTA IMPORTACIÓN ESTÉ
from app.database.database import SessionLocal
from app.database.models import User, LegalCase, Invoice, Agenda  # ← ASEGURAR QUE Agenda ESTÉ
from app.database.enums import InvoiceStatusEnum

class DashboardService:
    @staticmethod
    def get_metrics(user: User):
        """Obtiene métricas para el dashboard del usuario"""
        with SessionLocal() as session:
            # Obtener casos del usuario
            user_cases = (
                session.query(LegalCase)
                .filter(LegalCase.users.any(User.id == user.id))
                .all()
            )
            
            # Obtener facturas del usuario
            user_invoices = (
                session.query(Invoice)
                .filter(Invoice.issued_by_user_id == user.id)
                .all()
            )
            
            # AGREGAR ESTA SECCIÓN COMPLETA:
            # Obtener eventos de hoy del usuario
            today = date.today()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            today_events = (
                session.query(Agenda)
                .filter(
                    Agenda.user_id == user.id,
                    Agenda.account_id == user.account_id,
                    Agenda.due_date >= start_of_day,
                    Agenda.due_date <= end_of_day
                )
                .all()
            )
            
            # Calcular métricas
            active_cases = len([c for c in user_cases if c.status.lower() == "activo"])
            urgent_tasks = len([c for c in user_cases if c.status.lower() == "urgente"])
            pending_invoices = len([i for i in user_invoices if i.status == InvoiceStatusEnum.DUE])
            today_appointments = len(today_events)  # ← AHORA ESTA VARIABLE SÍ EXISTE
            
            return {
                "active_cases": active_cases,
                "pending_invoices": pending_invoices,
                "today_appointments": today_appointments,
                "urgent_tasks": urgent_tasks
            }
    
    @staticmethod
    def get_recent_cases(user: User):
        """Obtiene casos recientes para el dashboard"""
        with SessionLocal() as session:
            cases = (
                session.query(LegalCase)
                .options(joinedload(LegalCase.client))
                .filter(LegalCase.users.any(User.id == user.id))
                .order_by(LegalCase.start_date.desc())
                .limit(5)  # Límite por defecto
                .all()
            )
            
            case_summaries = []
            for case in cases:
                case_summaries.append({
                    "id": case.id,
                    "title": case.title,
                    "case_number": case.case_number or f"CASE-{case.id}",
                    "case_type": case.case_type,
                    "status": case.status,
                    "client_name": f"{case.client.first_name} {case.client.last_name}" if case.client else "Sin cliente",
                    "start_date": case.start_date.strftime("%Y-%m-%d")
                })
            
            return {
                "cases": case_summaries,
                "total_count": len(case_summaries)
            }