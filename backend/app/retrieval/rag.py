from typing import List, Dict, Any
from backend.app.retrieval.indexer import global_vector_store, build_knowledge_index


def query_knowledge_base(query: str, tenant_id: str = "ALL", top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search indexed knowledge base documents with tenant isolation.
    If the index is empty, build it automatically.
    """
    if len(global_vector_store.chunks) == 0:
        build_knowledge_index()

    results = global_vector_store.search(query=query, tenant_id=tenant_id, top_k=top_k)
    return results
