import os
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal, init_db
from backend.app.models.tenant import Tenant
from backend.app.models.user import User, UserRole
from backend.app.models.customer import Customer
from backend.app.models.order import Order, OrderStatus
from backend.app.models.payment import Payment, PaymentStatus
from backend.app.models.ticket import SupportTicket, TicketStatus, TicketPriority, Conversation, ConversationMessage
from backend.app.models.approval import ApprovalRequest, ApprovalAction, ApprovalStatus
from backend.app.models.audit import AuditEvent
from backend.app.security.auth import hash_password


def seed_all(db: Session = None):
    should_close = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close = True

    try:
        now = datetime.now(timezone.utc)

        # 1. Tenants
        tenant_nova = Tenant(id="tenant_nova", name="NovaStore Retail", slug="novastore", is_active=True)
        tenant_apex = Tenant(id="tenant_apex", name="ApexGadgets", slug="apexgadgets", is_active=True)
        db.merge(tenant_nova)
        db.merge(tenant_apex)
        db.commit()

        # 2. Users
        users = [
            # Tenant Nova
            User(id="usr-nova-admin", tenant_id="tenant_nova", email="admin@novastore.com", full_name="Nova Administrator", hashed_password=hash_password("admin123"), role=UserRole.ADMIN),
            User(id="usr-nova-approver", tenant_id="tenant_nova", email="sarah.approver@novastore.com", full_name="Sarah Jenkins (Support Lead)", hashed_password=hash_password("approver123"), role=UserRole.APPROVER),
            User(id="usr-nova-agent", tenant_id="tenant_nova", email="alex.agent@novastore.com", full_name="Alex Rivera (Agent)", hashed_password=hash_password("agent123"), role=UserRole.SUPPORT_AGENT),
            User(id="usr-nova-cust1", tenant_id="tenant_nova", email="john.doe@example.com", full_name="John Doe", hashed_password=hash_password("customer123"), role=UserRole.CUSTOMER),
            User(id="usr-nova-cust2", tenant_id="tenant_nova", email="maria.garcia@example.com", full_name="Maria Garcia", hashed_password=hash_password("customer123"), role=UserRole.CUSTOMER),
            # Tenant Apex
            User(id="usr-apex-admin", tenant_id="tenant_apex", email="admin@apexgadgets.com", full_name="Apex Admin", hashed_password=hash_password("admin123"), role=UserRole.ADMIN),
            User(id="usr-apex-cust1", tenant_id="tenant_apex", email="bob.smith@example.com", full_name="Bob Smith", hashed_password=hash_password("customer123"), role=UserRole.CUSTOMER),
        ]
        for u in users:
            db.merge(u)
        db.commit()

        # 3. Customers
        customers = [
            Customer(id="cust-nova-1", tenant_id="tenant_nova", user_id="usr-nova-cust1", name="John Doe", email="john.doe@example.com", phone="+1-555-0101", account_tier="gold"),
            Customer(id="cust-nova-2", tenant_id="tenant_nova", user_id="usr-nova-cust2", name="Maria Garcia", email="maria.garcia@example.com", phone="+1-555-0102", account_tier="standard"),
            Customer(id="cust-apex-1", tenant_id="tenant_apex", user_id="usr-apex-cust1", name="Bob Smith", email="bob.smith@example.com", phone="+1-555-0201", account_tier="standard"),
        ]
        for c in customers:
            db.merge(c)
        db.commit()

        # 4. Orders
        orders = [
            # ORD-1001: Under $50, delivered 5 days ago (Auto-refundable)
            Order(
                id="ord-1001",
                tenant_id="tenant_nova",
                customer_id="cust-nova-1",
                order_number="ORD-1001",
                status=OrderStatus.DELIVERED,
                total_amount=42.50,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="742 Evergreen Terrace, Springfield, OR 97477",
                carrier="USPS",
                tracking_number="94001118995625489001",
                placed_at=now - timedelta(days=9),
                delivered_at=now - timedelta(days=5),
                items_json=json.dumps([{"sku": "SKU-EARBUDS", "name": "Wireless Stereo Earbuds", "quantity": 1, "unit_price": 42.50}]),
            ),
            # ORD-1002: Over $50 ($129.99), delivered 3 days ago (Requires approval)
            Order(
                id="ord-1002",
                tenant_id="tenant_nova",
                customer_id="cust-nova-1",
                order_number="ORD-1002",
                status=OrderStatus.DELIVERED,
                total_amount=129.99,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="742 Evergreen Terrace, Springfield, OR 97477",
                carrier="FedEx",
                tracking_number="FDX-77492019920",
                placed_at=now - timedelta(days=7),
                delivered_at=now - timedelta(days=3),
                items_json=json.dumps([{"sku": "SKU-SMARTWATCH", "name": "Apex Pulse Pro Smartwatch", "quantity": 1, "unit_price": 129.99}]),
            ),
            # ORD-1003: Shipped / In Transit
            Order(
                id="ord-1003",
                tenant_id="tenant_nova",
                customer_id="cust-nova-1",
                order_number="ORD-1003",
                status=OrderStatus.SHIPPED,
                total_amount=85.00,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="742 Evergreen Terrace, Springfield, OR 97477",
                carrier="FedEx",
                tracking_number="FDX-99882211440",
                placed_at=now - timedelta(days=3),
                delivered_at=None,
                items_json=json.dumps([{"sku": "SKU-SPEAKER", "name": "Waterproof Bluetooth Speaker", "quantity": 1, "unit_price": 85.00}]),
            ),
            # ORD-1004: Delivered 45 days ago (Past 30-day window -> Ineligible)
            Order(
                id="ord-1004",
                tenant_id="tenant_nova",
                customer_id="cust-nova-1",
                order_number="ORD-1004",
                status=OrderStatus.DELIVERED,
                total_amount=60.00,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="742 Evergreen Terrace, Springfield, OR 97477",
                carrier="UPS",
                tracking_number="1Z9999999999999999",
                placed_at=now - timedelta(days=50),
                delivered_at=now - timedelta(days=45),
                items_json=json.dumps([{"sku": "SKU-KEYBOARD", "name": "Ergonomic Mechanical Keyboard", "quantity": 1, "unit_price": 60.00}]),
            ),
            # ORD-1005: Pending order for Maria Garcia
            Order(
                id="ord-1005",
                tenant_id="tenant_nova",
                customer_id="cust-nova-2",
                order_number="ORD-1005",
                status=OrderStatus.PENDING,
                total_amount=35.00,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="120 Main Street, Seattle, WA 98101",
                carrier="USPS",
                tracking_number=None,
                placed_at=now - timedelta(hours=4),
                delivered_at=None,
                items_json=json.dumps([{"sku": "SKU-CHARGER", "name": "65W USB-C GaN Fast Charger", "quantity": 1, "unit_price": 35.00}]),
            ),
            # ORD-1006: Failed payment inquiry
            Order(
                id="ord-1006",
                tenant_id="tenant_nova",
                customer_id="cust-nova-2",
                order_number="ORD-1006",
                status=OrderStatus.PROCESSING,
                total_amount=220.00,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="120 Main Street, Seattle, WA 98101",
                carrier=None,
                tracking_number=None,
                placed_at=now - timedelta(hours=2),
                delivered_at=None,
                items_json=json.dumps([{"sku": "SKU-HEADPHONES", "name": "Studio ANC Headphones", "quantity": 1, "unit_price": 220.00}]),
            ),
            # ORD-2001: Apex Gadgets order (Isolated in tenant_apex)
            Order(
                id="ord-2001",
                tenant_id="tenant_apex",
                customer_id="cust-apex-1",
                order_number="ORD-2001",
                status=OrderStatus.DELIVERED,
                total_amount=19.99,
                refunded_amount=0.0,
                currency="USD",
                shipping_address="500 Tech Blvd, Austin, TX 78701",
                carrier="DHL",
                tracking_number="DHL-55410928",
                placed_at=now - timedelta(days=4),
                delivered_at=now - timedelta(days=2),
                items_json=json.dumps([{"sku": "SKU-APEX-CABLE", "name": "Braided Thunderbolt 4 Cable", "quantity": 1, "unit_price": 19.99}]),
            ),
        ]
        for o in orders:
            db.merge(o)
        db.commit()

        # 5. Payments
        payments = [
            Payment(id="pay-1001", tenant_id="tenant_nova", order_id="ord-1001", customer_id="cust-nova-1", transaction_ref="txn-nova-1001", amount=42.50, currency="USD", status=PaymentStatus.CAPTURED, payment_method="credit_card", card_last4="4242"),
            Payment(id="pay-1002", tenant_id="tenant_nova", order_id="ord-1002", customer_id="cust-nova-1", transaction_ref="txn-nova-1002", amount=129.99, currency="USD", status=PaymentStatus.CAPTURED, payment_method="apple_pay", card_last4="8812"),
            Payment(id="pay-1003", tenant_id="tenant_nova", order_id="ord-1003", customer_id="cust-nova-1", transaction_ref="txn-nova-1003", amount=85.00, currency="USD", status=PaymentStatus.CAPTURED, payment_method="credit_card", card_last4="1092"),
            Payment(id="pay-1004", tenant_id="tenant_nova", order_id="ord-1004", customer_id="cust-nova-1", transaction_ref="txn-nova-1004", amount=60.00, currency="USD", status=PaymentStatus.CAPTURED, payment_method="credit_card", card_last4="4242"),
            Payment(id="pay-1005", tenant_id="tenant_nova", order_id="ord-1005", customer_id="cust-nova-2", transaction_ref="txn-nova-1005", amount=35.00, currency="USD", status=PaymentStatus.CAPTURED, payment_method="paypal"),
            Payment(id="pay-1006", tenant_id="tenant_nova", order_id="ord-1006", customer_id="cust-nova-2", transaction_ref="txn-nova-1006", amount=220.00, currency="USD", status=PaymentStatus.FAILED, payment_method="credit_card", card_last4="9911", failure_reason="ERR_INSUFFICIENT_FUNDS: Issuing cardholder account has insufficient funds."),
            Payment(id="pay-2001", tenant_id="tenant_apex", order_id="ord-2001", customer_id="cust-apex-1", transaction_ref="txn-apex-2001", amount=19.99, currency="USD", status=PaymentStatus.CAPTURED, payment_method="credit_card", card_last4="3322"),
        ]
        for p in payments:
            db.merge(p)
        db.commit()

        # 6. Sample Initial Ticket & Conversation
        tck_initial = SupportTicket(
            id="tck-1001",
            tenant_id="tenant_nova",
            customer_id="cust-nova-1",
            order_id="ord-1001",
            ticket_number="TCK-1001",
            title="Inquiry regarding Earbuds delivery",
            description="Customer asked for delivery status of their earbuds order.",
            status=TicketStatus.RESOLVED,
            priority=TicketPriority.LOW,
            category="order_status",
            resolution_summary="Verified package delivered via USPS on " + (now - timedelta(days=5)).strftime("%Y-%m-%d"),
            created_at=now - timedelta(days=5),
        )
        db.merge(tck_initial)
        db.commit()

        # Sample Pending Approval for Demo
        pending_appr = ApprovalRequest(
            id="appr-seed-001",
            tenant_id="tenant_nova",
            ticket_id="tck-1001",
            order_id="ord-1002",
            customer_id="cust-nova-1",
            requested_by="ai_agent",
            action_type=ApprovalAction.REFUND,
            requested_amount=129.99,
            currency="USD",
            reason="Customer reported defective hardware display on Smartwatch ORD-1002. Amount exceeds auto-refund threshold ($50.00).",
            status=ApprovalStatus.PENDING,
            idempotency_key="approval-seed-ord-1002-refund-129.99",
            created_at=now - timedelta(hours=1),
        )
        db.merge(pending_appr)
        db.commit()

        print("Successfully seeded synthetic database for multiple tenants!")
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    seed_all()
