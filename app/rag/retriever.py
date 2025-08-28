from typing import List, Dict, Tuple
import os, glob, re
from rank_bm25 import BM25Okapi
from app.config import settings
from app.rag.chunker import split_structured
from app.rag.store import VectorStore
from typing import List, Dict, Tuple
from rank_bm25 import BM25Okapi
from app.config import settings
from app.rag.chunker import split_structured
from app.rag.store import VectorStore
try:
    from sentence_transformers import CrossEncoder
    _RERANK_AVAILABLE = True
except Exception as _e:
    print("[RERANK] sentence-transformers not available:", _e)
    _RERANK_AVAILABLE = False
def _lex_overlap(q: str, text: str) -> float:
    qset = set(re.findall(r"\w+", q.lower()))
    tset = set(re.findall(r"\w+", text.lower()))
    if not qset or not tset:
        return 0.0
    inter = len(qset & tset)
    return round(inter / max(len(qset), 1), 4)

class HybridRetriever:
    def __init__(self):
        self.store = VectorStore(settings.INDEX_DIR)
        self.chunks, self.ids = self._load_chunks_from_store()
        self.bm25 = BM25Okapi([c.split() for c in self.chunks]) if self.chunks else None
        # NEW: init reranker (small, CPU-friendly)
        self.reranker = None
        if _RERANK_AVAILABLE:
            try:
                self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
                print("[RERANK] loaded ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                print("[RERANK] disabled:", e)
    def _load_chunks_from_store(self) -> Tuple[List[str], List[str]]:
        collected, ids = [], []
        for probe in ["the", "and", "a", "of"]:
            hits = self.store.query(probe, n_results=1000)
            for h in hits:
                if h["id"] not in ids:
                    ids.append(h["id"]); collected.append(h["text"])
        return collected, ids

    def retrieve(self, query: str, k: int = 6) -> List[Dict]:
        # gather a wider candidate set
        dense = self.store.query(query, n_results=k*6)
        dense_pairs = [(d["text"], d["id"]) for d in dense]

        sparse_pairs = []
        if self.bm25 is not None:
            scores = self.bm25.get_scores(query.split())
            idxs = sorted(range(len(self.chunks)), key=lambda i: -scores[i])[:k*6]
            sparse_pairs = [(self.chunks[i], self.ids[i]) for i in idxs]

        candidates, seen = [], set()
        for doc, id_ in dense_pairs + sparse_pairs:
            if id_ in seen: 
                continue
            seen.add(id_)
            candidates.append({"id": id_, "text": doc})

        # NEW: rerank if available
        if self.reranker and candidates:
            pairs = [(query, c["text"]) for c in candidates]
            scores = self.reranker.predict(pairs)
            ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
            fused = [c for (c, s) in ranked[:k]]
        else:
            fused = candidates[:k]

        for item in fused:
            item["support"] = _lex_overlap(query, item["text"])
        return fused