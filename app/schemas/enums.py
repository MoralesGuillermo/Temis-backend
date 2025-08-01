"""App/Database enums"""
from enum import Enum

# This enum can also be used for FileStatus and UserStatus
class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class AccountStatus(str, Enum):
    RUNNING = "RUNNING"
    DELETED = "DELETED"
    PAYMENT_DUE = "PAYMENT_DUE"

class InvoiceStatus(str, Enum):
    PAYED = "PAYED"
    DUE = "DUE"
    OVERDUE = "OVERDUE"

class CaseTypeLegalCase(str, Enum):
    CIVIL = "CIVIL"
    PENAL = "PENAL"
    LABORAL = "LABORAL"
    CONTENCIOSO_ADMINISTRATIVO = "CONTENCIOSO_ADMINISTRATIVO"
    MERCANTIL = "MERCANTIL"
    RECLAMOS_MENORES = "RECLAMOS_MENORES"
    FAMILIA = "FAMILIA"
    ADMINISTRATIVO = "ADMINISTRATIVO"
    FISCAL = "FISCAL"
    CONSTITUCIONAL = "CONSTITUCIONAL"
    AMBIENTAL = "AMBIENTAL"
    INTERNACIONAL = "INTERNACIONAL"

class PriorityLevelLegalCase(str, Enum):
    NORMAL = "NORMAL"
    MID = "MID"
    HIGH = "HIGH"

class StatusLegalCase(str, Enum):
    VICTORIA = "VICTORIA"
    DERROTA = "DERROTA"
    ACTIVO = "ACTIVO"
    CONCILIACION = "CONCILIACION"
