from backend.app.retrieval.indexer import build_knowledge_index

if __name__ == "__main__":
    store = build_knowledge_index()
    print(f"Knowledge index built successfully! Total chunks indexed: {len(store.chunks)}")
