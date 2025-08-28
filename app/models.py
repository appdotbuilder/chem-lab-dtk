from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


# Enums for various status types
class UserRole(str, Enum):
    ADMIN = "admin"
    LAB_HEAD = "lab_head"
    LAB_ASSISTANT = "lab_assistant"
    LECTURER = "lecturer"
    STUDENT = "student"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"


class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    MAINTENANCE = "maintenance"
    DAMAGED = "damaged"
    RETIRED = "retired"


class EquipmentCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"


class LoanRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHECKED_OUT = "checked_out"
    RETURNED = "returned"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    LOAN_REQUEST = "loan_request"
    LOAN_APPROVAL = "loan_approval"
    LOAN_REJECTION = "loan_rejection"
    CHECKOUT_REMINDER = "checkout_reminder"
    RETURN_REMINDER = "return_reminder"
    OVERDUE_WARNING = "overdue_warning"
    EQUIPMENT_MAINTENANCE = "equipment_maintenance"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    CHECKOUT = "checkout"
    RETURN = "return"


# User Management Models
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=100, index=True)
    email: str = Field(unique=True, max_length=255, index=True)
    full_name: str = Field(max_length=200)
    student_id: Optional[str] = Field(default=None, max_length=50, unique=True)
    employee_id: Optional[str] = Field(default=None, max_length=50, unique=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.STUDENT)
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION)
    department: Optional[str] = Field(default=None, max_length=100)
    year_level: Optional[int] = Field(default=None)  # For students
    hashed_password: str = Field(max_length=255)
    profile_picture: Optional[str] = Field(default=None, max_length=500)
    last_login: Optional[datetime] = Field(default=None)
    verification_token: Optional[str] = Field(default=None, max_length=100)
    reset_token: Optional[str] = Field(default=None, max_length=100)
    reset_token_expires: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    loan_requests: List["LoanRequest"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="user")
    managed_labs: List["Lab"] = Relationship(back_populates="manager")


# Laboratory Management Models
class Lab(SQLModel, table=True):
    __tablename__ = "labs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    code: str = Field(unique=True, max_length=50, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    location: str = Field(max_length=300)
    capacity: int = Field(default=0)
    manager_id: Optional[int] = Field(default=None, foreign_key="users.id")
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    operating_hours: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    safety_protocols: Optional[str] = Field(default=None, max_length=2000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    manager: Optional[User] = Relationship(back_populates="managed_labs")
    equipment: List["Equipment"] = Relationship(back_populates="lab")
    categories: List["EquipmentCategory"] = Relationship(back_populates="lab")


class EquipmentCategory(SQLModel, table=True):
    __tablename__ = "equipment_categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    lab_id: int = Field(foreign_key="labs.id")
    parent_category_id: Optional[int] = Field(default=None, foreign_key="equipment_categories.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lab: Lab = Relationship(back_populates="categories")
    parent_category: Optional["EquipmentCategory"] = Relationship(
        sa_relationship_kwargs={"remote_side": "EquipmentCategory.id"}
    )
    equipment: List["Equipment"] = Relationship(back_populates="category")


class Equipment(SQLModel, table=True):
    __tablename__ = "equipment"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    code: str = Field(unique=True, max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100, unique=True)
    category_id: int = Field(foreign_key="equipment_categories.id")
    lab_id: int = Field(foreign_key="labs.id")
    status: EquipmentStatus = Field(default=EquipmentStatus.AVAILABLE)
    condition: EquipmentCondition = Field(default=EquipmentCondition.GOOD)
    purchase_date: Optional[datetime] = Field(default=None)
    purchase_price: Optional[Decimal] = Field(default=Decimal("0"), decimal_places=2, max_digits=12)
    warranty_expires: Optional[datetime] = Field(default=None)
    location_in_lab: Optional[str] = Field(default=None, max_length=200)
    specifications: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    maintenance_schedule: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    usage_instructions: Optional[str] = Field(default=None, max_length=2000)
    safety_notes: Optional[str] = Field(default=None, max_length=2000)
    image_urls: List[str] = Field(default=[], sa_column=Column(JSON))
    qr_code: Optional[str] = Field(default=None, max_length=500)
    max_loan_duration_days: int = Field(default=7)
    requires_training: bool = Field(default=False)
    is_consumable: bool = Field(default=False)
    quantity_available: int = Field(default=1)
    quantity_total: int = Field(default=1)
    minimum_stock_level: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: EquipmentCategory = Relationship(back_populates="equipment")
    lab: Lab = Relationship(back_populates="equipment")
    loan_requests: List["LoanRequest"] = Relationship(back_populates="equipment")
    maintenance_records: List["MaintenanceRecord"] = Relationship(back_populates="equipment")


class MaintenanceRecord(SQLModel, table=True):
    __tablename__ = "maintenance_records"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    equipment_id: int = Field(foreign_key="equipment.id")
    maintenance_type: str = Field(max_length=100)  # preventive, corrective, calibration
    description: str = Field(max_length=1000)
    performed_by: str = Field(max_length=200)
    performed_date: datetime = Field(default_factory=datetime.utcnow)
    cost: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    next_maintenance_date: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=2000)
    attachments: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    equipment: Equipment = Relationship(back_populates="maintenance_records")


# Loan Management Models
class LoanRequest(SQLModel, table=True):
    __tablename__ = "loan_requests"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    request_number: str = Field(unique=True, max_length=50, index=True)
    user_id: int = Field(foreign_key="users.id")
    equipment_id: int = Field(foreign_key="equipment.id")
    quantity_requested: int = Field(default=1)
    purpose: str = Field(max_length=1000)
    course_name: Optional[str] = Field(default=None, max_length=200)
    instructor_name: Optional[str] = Field(default=None, max_length=200)
    requested_start_date: datetime
    requested_end_date: datetime
    status: LoanRequestStatus = Field(default=LoanRequestStatus.PENDING)
    priority: int = Field(default=1)  # 1=low, 2=medium, 3=high
    approved_by: Optional[int] = Field(default=None, foreign_key="users.id")
    approved_at: Optional[datetime] = Field(default=None)
    approval_notes: Optional[str] = Field(default=None, max_length=1000)
    rejected_reason: Optional[str] = Field(default=None, max_length=1000)
    actual_checkout_date: Optional[datetime] = Field(default=None)
    actual_return_date: Optional[datetime] = Field(default=None)
    checkout_condition: Optional[EquipmentCondition] = Field(default=None)
    return_condition: Optional[EquipmentCondition] = Field(default=None)
    checkout_notes: Optional[str] = Field(default=None, max_length=1000)
    return_notes: Optional[str] = Field(default=None, max_length=1000)
    late_fee: Optional[Decimal] = Field(default=Decimal("0"), decimal_places=2, max_digits=8)
    damage_fee: Optional[Decimal] = Field(default=Decimal("0"), decimal_places=2, max_digits=8)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="loan_requests")
    equipment: Equipment = Relationship(back_populates="loan_requests")


# Notification System Models
class Notification(SQLModel, table=True):
    __tablename__ = "notifications"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    type: NotificationType
    title: str = Field(max_length=300)
    message: str = Field(max_length=1000)
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Additional context data
    is_read: bool = Field(default=False)
    is_email_sent: bool = Field(default=False)
    priority: int = Field(default=1)  # 1=low, 2=medium, 3=high
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="notifications")


# Audit Trail Models
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: AuditAction
    table_name: str = Field(max_length=100)
    record_id: Optional[int] = Field(default=None)
    old_values: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    new_values: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    session_id: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="audit_logs")


# Content Management Models
class ContentPage(SQLModel, table=True):
    __tablename__ = "content_pages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, max_length=200, index=True)
    title: str = Field(max_length=300)
    content: str  # HTML content
    meta_description: Optional[str] = Field(default=None, max_length=500)
    meta_keywords: Optional[str] = Field(default=None, max_length=500)
    is_published: bool = Field(default=False)
    language: str = Field(default="id", max_length=5)  # Indonesian by default
    author_id: Optional[int] = Field(default=None, foreign_key="users.id")
    published_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# System Configuration Models
class SystemSetting(SQLModel, table=True):
    __tablename__ = "system_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, max_length=100, index=True)
    value: str = Field(max_length=2000)
    description: Optional[str] = Field(default=None, max_length=500)
    data_type: str = Field(max_length=50)  # string, integer, boolean, json, decimal
    category: str = Field(max_length=100)
    is_public: bool = Field(default=False)  # Can be accessed without authentication
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Reporting Models
class Report(SQLModel, table=True):
    __tablename__ = "reports"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=300)
    description: Optional[str] = Field(default=None, max_length=1000)
    report_type: str = Field(max_length=100)  # equipment_usage, user_activity, overdue_loans, etc.
    parameters: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    generated_by: int = Field(foreign_key="users.id")
    file_path: Optional[str] = Field(default=None, max_length=500)
    file_size: Optional[int] = Field(default=None)
    status: str = Field(max_length=50, default="pending")  # pending, generating, completed, failed
    error_message: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)


# Non-persistent schemas for validation and API
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=100)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=200)
    password: str = Field(min_length=8)
    student_id: Optional[str] = Field(default=None, max_length=50)
    employee_id: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.STUDENT)
    department: Optional[str] = Field(default=None, max_length=100)
    year_level: Optional[int] = Field(default=None)


class UserUpdate(SQLModel, table=False):
    full_name: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    department: Optional[str] = Field(default=None, max_length=100)
    year_level: Optional[int] = Field(default=None)
    profile_picture: Optional[str] = Field(default=None, max_length=500)


class EquipmentCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    code: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    category_id: int
    lab_id: int
    condition: EquipmentCondition = Field(default=EquipmentCondition.GOOD)
    purchase_date: Optional[datetime] = Field(default=None)
    purchase_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    warranty_expires: Optional[datetime] = Field(default=None)
    location_in_lab: Optional[str] = Field(default=None, max_length=200)
    specifications: Dict[str, Any] = Field(default={})
    usage_instructions: Optional[str] = Field(default=None, max_length=2000)
    safety_notes: Optional[str] = Field(default=None, max_length=2000)
    max_loan_duration_days: int = Field(default=7)
    requires_training: bool = Field(default=False)
    is_consumable: bool = Field(default=False)
    quantity_total: int = Field(default=1)
    minimum_stock_level: int = Field(default=0)


class EquipmentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    category_id: Optional[int] = Field(default=None)
    status: Optional[EquipmentStatus] = Field(default=None)
    condition: Optional[EquipmentCondition] = Field(default=None)
    location_in_lab: Optional[str] = Field(default=None, max_length=200)
    specifications: Optional[Dict[str, Any]] = Field(default=None)
    usage_instructions: Optional[str] = Field(default=None, max_length=2000)
    safety_notes: Optional[str] = Field(default=None, max_length=2000)
    max_loan_duration_days: Optional[int] = Field(default=None)
    requires_training: Optional[bool] = Field(default=None)
    quantity_total: Optional[int] = Field(default=None)
    minimum_stock_level: Optional[int] = Field(default=None)


class LoanRequestCreate(SQLModel, table=False):
    equipment_id: int
    quantity_requested: int = Field(default=1)
    purpose: str = Field(max_length=1000)
    course_name: Optional[str] = Field(default=None, max_length=200)
    instructor_name: Optional[str] = Field(default=None, max_length=200)
    requested_start_date: datetime
    requested_end_date: datetime
    priority: int = Field(default=1)


class LoanRequestUpdate(SQLModel, table=False):
    status: Optional[LoanRequestStatus] = Field(default=None)
    approval_notes: Optional[str] = Field(default=None, max_length=1000)
    rejected_reason: Optional[str] = Field(default=None, max_length=1000)
    checkout_condition: Optional[EquipmentCondition] = Field(default=None)
    return_condition: Optional[EquipmentCondition] = Field(default=None)
    checkout_notes: Optional[str] = Field(default=None, max_length=1000)
    return_notes: Optional[str] = Field(default=None, max_length=1000)


class LabCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    code: str = Field(max_length=50)
    description: Optional[str] = Field(default=None, max_length=1000)
    location: str = Field(max_length=300)
    capacity: int = Field(default=0)
    manager_id: Optional[int] = Field(default=None)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    operating_hours: Dict[str, Any] = Field(default={})
    safety_protocols: Optional[str] = Field(default=None, max_length=2000)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    lab_id: int
    parent_category_id: Optional[int] = Field(default=None)


class NotificationCreate(SQLModel, table=False):
    user_id: int
    type: NotificationType
    title: str = Field(max_length=300)
    message: str = Field(max_length=1000)
    data: Dict[str, Any] = Field(default={})
    priority: int = Field(default=1)
    expires_at: Optional[datetime] = Field(default=None)


class MaintenanceRecordCreate(SQLModel, table=False):
    equipment_id: int
    maintenance_type: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    performed_by: str = Field(max_length=200)
    performed_date: datetime = Field(default_factory=datetime.utcnow)
    cost: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    next_maintenance_date: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=2000)


class ReportCreate(SQLModel, table=False):
    name: str = Field(max_length=300)
    description: Optional[str] = Field(default=None, max_length=1000)
    report_type: str = Field(max_length=100)
    parameters: Dict[str, Any] = Field(default={})
