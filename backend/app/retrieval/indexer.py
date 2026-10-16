import os
import re
from typing import List
from backend.app.retrieval.vector_store import DocumentChunk, SimpleVectorStore
from backend.app.config import settings

# Global vector store instance
global_vector_store = SimpleVectorStore()


def parse_markdown_document(file_path: str) -> List[DocumentChunk]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    filename = os.path.basename(file_path)
    category = "policies" if "policies" in file_path else "faqs"

    # Extract Doc ID and Title
    doc_id_match = re.search(r"Doc ID:\s*([^\n\r]+)", text)
    doc_id = doc_id_match.group(1).strip() if doc_id_match else filename.replace(".md", "").upper()

    title_match = re.search(r"^#\s+([^\n\r]+)", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename

    tenants_match = re.search(r"Applicable Tenants:\s*([^\n\r]+)", text)
    tenant_id = tenants_match.group(1).strip() if tenants_match else "ALL"

    # Split into sections by ## headers
    sections = re.split(r"(?=^##\s+)", text, flags=re.MULTILINE)
    chunks = []
    chunk_index = 0

    for sec in sections:
        sec_text = sec.strip()
        if not sec_text:
            continue

        sec_title_match = re.search(r"^##\s+([^\n\r]+)", sec_text)
        sec_title = sec_title_match.group(1).strip() if sec_title_match else title

        chunk = DocumentChunk(
            chunk_id=f"{doc_id}-chunk-{chunk_index}",
            doc_id=doc_id,
            title=f"{title} - {sec_title}" if sec_title != title else title,
            category=category,
            source_path=os.path.relpath(file_path, os.path.dirname(settings.KNOWLEDGE_BASE_DIR)),
            tenant_id=tenant_id,
            content=sec_text,
            metadata={
                "section": sec_title,
                "file_path": file_path,
                "chunk_index": chunk_index,
            }
        )
        chunks.append(chunk)
        chunk_index += 1

    return chunks


def build_knowledge_index(knowledge_dir: str = None) -> SimpleVectorStore:
    target_dir = knowledge_dir or settings.KNOWLEDGE_BASE_DIR
    all_chunks: List[DocumentChunk] = []

    if not os.path.exists(target_dir):
        # Fallback to relative path lookup
        target_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../knowledge_base")
        )

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    chunks = parse_markdown_document(file_path)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error parsing knowledge file {file_path}: {e}")

    global_vector_store.fit_and_index(all_chunks)
    return global_vector_store
