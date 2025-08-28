from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for various statuses
class UserRole(str, Enum):
    ADMIN = "admin"
    HEAD_LAB = "head_lab"
    LABORAN = "laboran"
    LECTURER = "lecturer"
    STUDENT = "student"


class UserStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"


class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    DAMAGED = "damaged"


class BorrowingStatus(str, Enum):
    PENDING = "pending"
    APPROVED_LABORAN = "approved_laboran"
    APPROVED_HEAD = "approved_head"
    CHECKED_OUT = "checked_out"
    CHECKED_IN = "checked_in"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"


class NotificationType(str, Enum):
    USER_REGISTRATION = "user_registration"
    USER_VERIFICATION = "user_verification"
    BORROWING_REQUEST = "borrowing_request"
    BORROWING_APPROVED = "borrowing_approved"
    BORROWING_REJECTED = "borrowing_rejected"
    EQUIPMENT_DUE = "equipment_due"
    EQUIPMENT_OVERDUE = "equipment_overdue"
    EQUIPMENT_RETURNED = "equipment_returned"
    EQUIPMENT_DAMAGED = "equipment_damaged"
    MAINTENANCE_SCHEDULED = "maintenance_scheduled"


class MaintenanceType(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"


class MaintenanceStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    CHECKOUT = "checkout"
    CHECKIN = "checkin"


# Persistent models (stored in database)


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    nim_nik: Optional[str] = Field(default=None, max_length=50)  # NIM for students, NIK for staff
    role: UserRole = Field(default=UserRole.STUDENT)
    status: UserStatus = Field(default=UserStatus.PENDING)
    phone: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)
    verified_at: Optional[datetime] = Field(default=None)
    verified_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships
    verified_by: Optional["User"] = Relationship(
        back_populates="verified_users", sa_relationship_kwargs={"remote_side": "User.id", "post_update": True}
    )
    verified_users: List["User"] = Relationship(back_populates="verified_by")
    borrowings: List["Borrowing"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="user")
    lab_memberships: List["LabMember"] = Relationship(back_populates="user")


class Lab(SQLModel, table=True):
    __tablename__ = "labs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    code: str = Field(unique=True, max_length=20)
    description: str = Field(default="")
    location: str = Field(max_length=200)
    capacity: int = Field(default=0)
    operating_hours: str = Field(default="")
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    rules_document: Optional[str] = Field(default=None)  # PDF file path
    sop_document: Optional[str] = Field(default=None)  # PDF file path
    gallery: List[str] = Field(default=[], sa_column=Column(JSON))  # Image file paths
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    equipment: List["Equipment"] = Relationship(back_populates="lab")
    members: List["LabMember"] = Relationship(back_populates="lab")


class LabMember(SQLModel, table=True):
    __tablename__ = "lab_members"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    lab_id: int = Field(foreign_key="labs.id")
    user_id: int = Field(foreign_key="users.id")
    role: str = Field(max_length=50)  # "head", "laboran", "member"
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lab: Lab = Relationship(back_populates="members")
    user: User = Relationship(back_populates="lab_memberships")


class EquipmentCategory(SQLModel, table=True):
    __tablename__ = "equipment_categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    equipment: List["Equipment"] = Relationship(back_populates="category")


class Equipment(SQLModel, table=True):
    __tablename__ = "equipment"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    code: str = Field(unique=True, max_length=50)
    category_id: int = Field(foreign_key="equipment_categories.id")
    lab_id: int = Field(foreign_key="labs.id")
    description: str = Field(default="")
    specifications: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    purchase_date: Optional[datetime] = Field(default=None)
    purchase_price: Optional[Decimal] = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    condition: str = Field(default="good")  # good, fair, poor
    status: EquipmentStatus = Field(default=EquipmentStatus.AVAILABLE)
    needs_head_approval: bool = Field(default=False)
    image_path: Optional[str] = Field(default=None)
    manual_document: Optional[str] = Field(default=None)  # PDF file path
    qr_code_path: Optional[str] = Field(default=None)
    maintenance_interval_days: int = Field(default=365)  # Days between maintenance
    last_maintenance: Optional[datetime] = Field(default=None)
    next_maintenance: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: EquipmentCategory = Relationship(back_populates="equipment")
    lab: Lab = Relationship(back_populates="equipment")
    borrowings: List["Borrowing"] = Relationship(back_populates="equipment")
    maintenance_records: List["MaintenanceRecord"] = Relationship(back_populates="equipment")
    availability_slots: List["EquipmentAvailability"] = Relationship(back_populates="equipment")


class EquipmentAvailability(SQLModel, table=True):
    __tablename__ = "equipment_availability"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    equipment_id: int = Field(foreign_key="equipment.id")
    date: datetime = Field()
    start_time: str = Field(max_length=5)  # HH:MM format
    end_time: str = Field(max_length=5)  # HH:MM format
    is_blocked: bool = Field(default=False)  # True if blocked for maintenance/other reasons
    block_reason: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    equipment: Equipment = Relationship(back_populates="availability_slots")


class Borrowing(SQLModel, table=True):
    __tablename__ = "borrowings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    equipment_id: int = Field(foreign_key="equipment.id")
    status: BorrowingStatus = Field(default=BorrowingStatus.PENDING)
    start_datetime: datetime = Field()
    end_datetime: datetime = Field()
    actual_return_datetime: Optional[datetime] = Field(default=None)
    purpose: str = Field(max_length=500)
    jsa_document: Optional[str] = Field(default=None)  # JSA PDF file path
    notes: str = Field(default="")

    # Approval tracking
    approved_by_laboran_id: Optional[int] = Field(default=None, foreign_key="users.id")
    approved_by_laboran_at: Optional[datetime] = Field(default=None)
    approved_by_head_id: Optional[int] = Field(default=None, foreign_key="users.id")
    approved_by_head_at: Optional[datetime] = Field(default=None)

    # Condition tracking
    condition_before: str = Field(default="good")
    condition_after: Optional[str] = Field(default=None)
    damage_report: Optional[str] = Field(default=None)

    # Check-in/out tracking
    checked_out_at: Optional[datetime] = Field(default=None)
    checked_out_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    checked_in_at: Optional[datetime] = Field(default=None)
    checked_in_by_id: Optional[int] = Field(default=None, foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="borrowings")
    equipment: Equipment = Relationship(back_populates="borrowings")


class MaintenanceRecord(SQLModel, table=True):
    __tablename__ = "maintenance_records"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    equipment_id: int = Field(foreign_key="equipment.id")
    maintenance_type: MaintenanceType = Field()
    status: MaintenanceStatus = Field(default=MaintenanceStatus.SCHEDULED)
    scheduled_date: datetime = Field()
    completed_date: Optional[datetime] = Field(default=None)
    performed_by: Optional[str] = Field(default=None, max_length=100)
    description: str = Field()
    cost: Optional[Decimal] = Field(default=Decimal("0"), max_digits=10, decimal_places=2)
    notes: str = Field(default="")
    attachments: List[str] = Field(default=[], sa_column=Column(JSON))  # File paths
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    equipment: Equipment = Relationship(back_populates="maintenance_records")


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    type: NotificationType = Field()
    title: str = Field(max_length=200)
    message: str = Field()
    status: NotificationStatus = Field(default=NotificationStatus.UNREAD)
    related_id: Optional[int] = Field(default=None)  # ID of related entity (borrowing, user, etc.)
    related_type: Optional[str] = Field(default=None, max_length=50)  # Type of related entity
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="notifications")


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: AuditAction = Field()
    entity_type: str = Field(max_length=50)  # Table/model name
    entity_id: Optional[int] = Field(default=None)
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="audit_logs")


class AppContent(SQLModel, table=True):
    __tablename__ = "app_content"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, max_length=100)  # landing_page_content, about_us, etc.
    content: str = Field()  # Markdown content
    content_type: str = Field(default="markdown", max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by_id: Optional[int] = Field(default=None, foreign_key="users.id")


class HelpTicket(SQLModel, table=True):
    __tablename__ = "help_tickets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    subject: str = Field(max_length=200)
    message: str = Field()
    status: str = Field(default="open", max_length=20)  # open, in_progress, resolved, closed
    priority: str = Field(default="normal", max_length=20)  # low, normal, high, urgent
    category: str = Field(default="general", max_length=50)  # general, password_reset, account, technical
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="users.id")
    resolved_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)


class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(max_length=100)
    nim_nik: Optional[str] = Field(default=None, max_length=50)
    role: UserRole = Field(default=UserRole.STUDENT)
    phone: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(SQLModel, table=False):
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    nim_nik: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: Optional[UserRole] = Field(default=None)
    status: Optional[UserStatus] = Field(default=None)


class UserLogin(SQLModel, table=False):
    email: str = Field(max_length=255)
    password: str = Field(min_length=1, max_length=100)


class PasswordReset(SQLModel, table=False):
    email: str = Field(max_length=255)
    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)


class LabCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    code: str = Field(max_length=20)
    description: str = Field(default="")
    location: str = Field(max_length=200)
    capacity: int = Field(default=0)
    operating_hours: str = Field(default="")
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=20)


class LabUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    code: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=200)
    capacity: Optional[int] = Field(default=None)
    operating_hours: Optional[str] = Field(default=None)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None)


class EquipmentCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    code: str = Field(max_length=50)
    category_id: int
    lab_id: int
    description: str = Field(default="")
    specifications: Dict[str, Any] = Field(default={})
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    purchase_date: Optional[datetime] = Field(default=None)
    purchase_price: Optional[Decimal] = Field(default=Decimal("0"))
    condition: str = Field(default="good")
    needs_head_approval: bool = Field(default=False)
    maintenance_interval_days: int = Field(default=365)


class EquipmentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    category_id: Optional[int] = Field(default=None)
    lab_id: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    specifications: Optional[Dict[str, Any]] = Field(default=None)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    condition: Optional[str] = Field(default=None)
    status: Optional[EquipmentStatus] = Field(default=None)
    needs_head_approval: Optional[bool] = Field(default=None)
    maintenance_interval_days: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class BorrowingCreate(SQLModel, table=False):
    equipment_id: int
    start_datetime: datetime
    end_datetime: datetime
    purpose: str = Field(max_length=500)
    notes: str = Field(default="")


class BorrowingUpdate(SQLModel, table=False):
    status: Optional[BorrowingStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    condition_after: Optional[str] = Field(default=None)
    damage_report: Optional[str] = Field(default=None)


class NotificationCreate(SQLModel, table=False):
    user_id: int
    type: NotificationType
    title: str = Field(max_length=200)
    message: str
    related_id: Optional[int] = Field(default=None)
    related_type: Optional[str] = Field(default=None, max_length=50)


class MaintenanceRecordCreate(SQLModel, table=False):
    equipment_id: int
    maintenance_type: MaintenanceType
    scheduled_date: datetime
    description: str
    performed_by: Optional[str] = Field(default=None, max_length=100)
    cost: Optional[Decimal] = Field(default=Decimal("0"))
    notes: str = Field(default="")


class MaintenanceRecordUpdate(SQLModel, table=False):
    status: Optional[MaintenanceStatus] = Field(default=None)
    completed_date: Optional[datetime] = Field(default=None)
    performed_by: Optional[str] = Field(default=None, max_length=100)
    cost: Optional[Decimal] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class HelpTicketCreate(SQLModel, table=False):
    subject: str = Field(max_length=200)
    message: str
    priority: str = Field(default="normal", max_length=20)
    category: str = Field(default="general", max_length=50)


class HelpTicketUpdate(SQLModel, table=False):
    status: Optional[str] = Field(default=None, max_length=20)
    assigned_to_id: Optional[int] = Field(default=None)


class AppContentUpdate(SQLModel, table=False):
    content: str
    content_type: str = Field(default="markdown", max_length=20)
    is_active: bool = Field(default=True)


# Statistics and reporting schemas


class EquipmentUsageStats(SQLModel, table=False):
    equipment_id: int
    equipment_name: str
    total_borrowings: int
    total_hours: float
    average_duration: float
    damage_reports: int
    overdue_count: int


class UserBorrowingStats(SQLModel, table=False):
    user_id: int
    user_name: str
    total_borrowings: int
    completed_borrowings: int
    overdue_count: int
    damage_reports: int


class LabUsageStats(SQLModel, table=False):
    lab_id: int
    lab_name: str
    total_equipment: int
    total_borrowings: int
    utilization_rate: float
    average_booking_duration: float


class PeriodStats(SQLModel, table=False):
    period: str  # "2024-01", "2024-Q1", etc.
    total_borrowings: int
    completed_borrowings: int
    overdue_count: int
    damage_reports: int
    unique_users: int
    unique_equipment: int
