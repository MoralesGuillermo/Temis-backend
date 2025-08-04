from enum import Enum


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
   


class AccountStatusEnum(str, Enum):
    RUNNING = "running"
    DELETED = "deleted"
    PAYMENT_DUE = "payment due"


class PriorityLevelEnum(str, Enum):
    NORMAL = "normal"
    MID = "mid"
    HIGH = "high"


class LegalCaseStatusEnum(str, Enum):
    VICTORIA = "victoria"
    DERROTA = "derrota"
    ACTIVO = "activo"
    CONCILIACION = "conciliacion"


class CaseTypeEnum(str, Enum):
    CIVIL = "civil"
    PENAL = "penal"
    LABORAL = "laboral"
    CONTENCIOSO_ADMINISTRATIVO = "contencioso-administrativo"
    MERCANTIL = "mercantil"
    RECLAMOS_MENORES = "reclamos menores"
    FAMILIA = "familia"
    ADMINISTRATIVO = "administrativo"
    FISCAL = "fiscal"
    CONSTITUCIONAL = "constitucional"
    AMBIENTAL = "ambiental"
    INTERNACIONAL = "internacional"


class InvoiceStatusEnum(str, Enum):
    PAYED = "PAYED"        # Se mostrará como "Pagado" en el frontend
    DUE = "DUE"            # Se mostrará como "Pendiente"
    OVERDUE = "OVERDUE"    # Se mostrará como "Vencida"