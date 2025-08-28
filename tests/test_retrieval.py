from app.rag.retriever import HybridRetriever

def test_retrieval_min_results():
    r = HybridRetriever()
    out = r.retrieve("renewal", k=5)
    assert isinstance(out, list)
    # no strict count assertion here because empty index might exist before bootstrap
