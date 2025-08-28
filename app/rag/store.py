from typing import List, Dict
import chromadb
from chromadb.config import Settings as ChromaSettings

class VectorStore:
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(path=persist_dir, settings=ChromaSettings(allow_reset=True))
        self.col = self.client.get_or_create_collection(name="rag_demo")
    def add(self, ids: List[str], texts: List[str], metadatas: List[Dict] | None = None):
        self.col.add(ids=ids, documents=texts, metadatas=metadatas or [{} for _ in ids])
    def count(self) -> int:
        return self.col.count()
    def query(self, query_text: str, n_results: int = 10) -> List[Dict]:
        out = self.col.query(query_texts=[query_text], n_results=n_results)
        docs = out.get("documents", [[]])[0]
        ids = out.get("ids", [[]])[0]
        metas = out.get("metadatas", [[]])[0]
        return [{"id": i, "text": d, "meta": m} for d,i,m in zip(docs, ids, metas)]
