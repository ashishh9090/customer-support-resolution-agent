import os
import re
import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    category: str
    source_path: str
    tenant_id: str = "ALL"
    content: str
    metadata: Dict[str, Any] = {}
    tf_vector: Dict[str, float] = {}


STOP_WORDS = {
    "a", "an", "the", "and", "or", "is", "was", "are", "were", "in", "on", "at",
    "to", "for", "of", "with", "by", "my", "your", "i", "you", "it", "this", "that",
    "do", "how", "what", "why", "when", "where", "can", "have", "has", "had", "be"
}


class SimpleVectorStore:
    """
    Deterministic TF-IDF & BM25 hybrid semantic retrieval store with tenant isolation.
    """

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.doc_freq: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.total_docs: int = 0

    def _stem(self, word: str) -> str:
        if len(word) > 4:
            if word.endswith("ed") or word.endswith("es"):
                return word[:-2]
            if word.endswith("ing"):
                return word[:-3]
            if word.endswith("s") and not word.endswith("ss"):
                return word[:-1]
        return word

    def _tokenize(self, text: str) -> List[str]:
        raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())
        tokens = [self._stem(t) for t in raw_tokens if t not in STOP_WORDS]
        return tokens or raw_tokens

    def fit_and_index(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.total_docs = len(chunks)
        if self.total_docs == 0:
            return

        self.doc_freq = {}
        for chunk in chunks:
            text = f"{chunk.title} {chunk.title} {chunk.content}"
            seen_tokens = set(self._tokenize(text))
            for t in seen_tokens:
                self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

        self.idf = {
            t: math.log((self.total_docs + 1) / (df + 1)) + 1.0
            for t, df in self.doc_freq.items()
        }

        # Precompute normalized TF-IDF vectors for each chunk
        for chunk in self.chunks:
            text = f"{chunk.title} {chunk.title} {chunk.content}"
            tokens = self._tokenize(text)
            tf_raw = {}
            for t in tokens:
                tf_raw[t] = tf_raw.get(t, 0) + 1

            vec = {}
            sum_sq = 0.0
            for t, count in tf_raw.items():
                w = (1.0 + math.log(count)) * self.idf.get(t, 1.0)
                vec[t] = w
                sum_sq += w * w

            norm = math.sqrt(sum_sq) if sum_sq > 0 else 1.0
            chunk.tf_vector = {t: w / norm for t, w in vec.items()}

    def search(
        self,
        query: str,
        tenant_id: str = "ALL",
        top_k: int = 3,
        min_score: float = 0.05
    ) -> List[Dict[str, Any]]:
        q_tokens = self._tokenize(query)
        if not q_tokens or not self.chunks:
            return []

        # Query TF-IDF vector
        q_tf = {}
        for t in q_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1

        q_vec = {}
        sum_sq = 0.0
        for t, count in q_tf.items():
            w = (1.0 + math.log(count)) * self.idf.get(t, 1.0)
            q_vec[t] = w
            sum_sq += w * w

        q_norm = math.sqrt(sum_sq) if sum_sq > 0 else 1.0
        q_norm_vec = {t: w / q_norm for t, w in q_vec.items()}
        q_set = set(q_tokens)

        scored = []
        for chunk in self.chunks:
            if chunk.tenant_id != "ALL" and chunk.tenant_id != tenant_id:
                continue

            # Dot product of normalized vectors = Cosine similarity
            dot_product = sum(w * chunk.tf_vector.get(t, 0.0) for t, w in q_norm_vec.items())

            # Title matching boost
            title_tokens = set(self._tokenize(chunk.title))
            title_overlap = len(q_set.intersection(title_tokens))
            title_bonus = (title_overlap / len(q_set)) * 0.5 if q_set else 0.0

            total_score = dot_product * 0.7 + title_bonus * 0.3

            if total_score >= min_score or title_overlap > 0:
                scored.append({
                    "score": round(total_score, 4),
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "title": chunk.title,
                    "category": chunk.category,
                    "source_path": chunk.source_path,
                    "tenant_id": chunk.tenant_id,
                    "content": chunk.content,
                    "citation": f"[{chunk.title} ({chunk.doc_id})]",
                    "metadata": chunk.metadata,
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
