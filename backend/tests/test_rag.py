import pytest
from backend.app.retrieval.rag import query_knowledge_base
from backend.app.retrieval.indexer import global_vector_store


def test_knowledge_base_indexing():
    assert len(global_vector_store.chunks) > 0
    categories = {c.category for c in global_vector_store.chunks}
    assert "policies" in categories
    assert "faqs" in categories


def test_query_shipping_policy():
    results = query_knowledge_base("What are standard shipping delivery times?", tenant_id="tenant_nova")
    assert len(results) > 0
    top = results[0]
    assert "Shipping" in top["title"]
    assert "POL-SHIP-001" in top["citation"]


def test_query_refund_policy():
    results = query_knowledge_base("return window and refund rules", tenant_id="tenant_nova")
    assert len(results) > 0
    top = results[0]
    assert "Refund" in top["title"] or "Return" in top["title"]


def test_query_payment_troubleshooting():
    results = query_knowledge_base("Why was my credit card declined?", tenant_id="tenant_nova")
    assert len(results) > 0
    top = results[0]
    assert "Payment" in top["title"]
