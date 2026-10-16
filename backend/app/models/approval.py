import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base


class ApprovalAction(str, enum.Enum):
    REFUND = "REFUND"
    REPLACEMENT = "REPLACEMENT"
    POLICY_OVERRIDE = "POLICY_OVERRIDE"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("support_tickets.id", ondelete="CASCADE"), index=True, nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), nullable=True)
    customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(64), default="ai_agent", nullable=False)
    action_type: Mapped[ApprovalAction] = mapped_column(
        Enum(ApprovalAction, values_callable=lambda x: [e.value for e in x]),
        default=ApprovalAction.REFUND,
        nullable=False
    )
    requested_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_data: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, values_callable=lambda x: [e.value for e in x]),
        default=ApprovalStatus.PENDING,
        nullable=False
    )
    reviewed_by: Mapped[str] = mapped_column(String(64), nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="approvals")
