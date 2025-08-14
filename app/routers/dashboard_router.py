from fastapi import HTTPException, status, APIRouter, Request
from app.services.AuthService import AuthService 
from app.services.DashboardService import DashboardService
from app.schemas.LegalCaseSummaryResponse import LegalCaseSummaryResponse
from app.schemas.DashboardMetricsResponse import DashboardMetricsResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

UNAUTHORIZED_MSG = "Usuario no autenticado. Debe inicar sesión para poder visualizar este recurso."

@router.get("/metrics", status_code=status.HTTP_200_OK, response_model=DashboardMetricsResponse, description="Obtiene métricas para el dashboard")
def get_dashboard_metrics(request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    
    metrics = DashboardService.get_metrics(user)
    return metrics

@router.get("/recent-cases", status_code=status.HTTP_200_OK, response_model=LegalCaseSummaryResponse, description="Obtiene casos recientes para el dashboard")
def get_recent_cases(request: Request):
    jwt = request.cookies.get("accessToken")
    user = AuthService.get_active_user(jwt)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED_MSG)
    
    cases = DashboardService.get_recent_cases(user)
    return cases