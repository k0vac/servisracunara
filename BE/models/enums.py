import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TECHNICIAN = "technician"


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_PAYMENT = "awaiting_payment"
    CLOSED = "closed"


class CasePriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    URGENT = "urgent"


class CaseEventType(str, enum.Enum):
    NOTE = "note"
    DIAGNOSIS = "diagnosis"
    REPAIR = "repair"
    PART_USED = "part_used"


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class InvoiceLineItemSource(str, enum.Enum):
    MATERIAL = "material"
    LABOR = "labor"
    FEE = "fee"
    DISCOUNT = "discount"
