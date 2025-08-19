from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class TenantStatus(str, Enum):
    """Tenant lifecycle statuses"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CLOSED = "closed"


class TransferStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    IN_TRANSIT = "in_transit"


class TenantTier(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    EXTRA_USER = "extra_user"
    EXTRA_STORE = "extra_store"

class StockStatus(str, Enum):
    ACTIVE = "active"
    QUARANTINED = "quarantined"
    RESERVED = "reserved"
    DAMAGED = "damaged"

class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class LogLevel(str):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SECURITY = "SECURITY"
    PERMANENT_DELETE = "PERMANENT_DELETE"