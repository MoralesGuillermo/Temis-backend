from pydantic import BaseModel

class DashboardMetricsResponse(BaseModel):
    active_cases: int
    pending_invoices: int
    today_appointments: int
    urgent_tasks: int