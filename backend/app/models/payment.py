import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(64), ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False)
    transaction_ref: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x]),
        default=PaymentStatus.CAPTURED,
        nullable=False
    )
    payment_method: Mapped[str] = mapped_column(String(64), default="credit_card", nullable=False)
    card_last4: Mapped[str] = mapped_column(String(4), nullable=True)
    failure_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    gateway_response_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    order = relationship("Order", back_populates="payments")
