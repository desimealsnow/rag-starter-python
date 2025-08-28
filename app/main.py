from fastapi import FastAPI
from pydantic import BaseModel
from app.rag.retriever import HybridRetriever
from app.rag.llm import LLMClient
from app.rag.evaluator import simple_judge
from app.rag.faithfulness import is_faithful

import re

app = FastAPI(title="RAG Starter API", version="0.1.1")

retriever = HybridRetriever()
llm = LLMClient()

class AskBody(BaseModel):
    question: str

@app.get('/health')
def health():
    return {'ok': True}

@app.post('/ask')
def ask(body: AskBody):
    q = body.question.strip()
    hits = retriever.retrieve(q, k=6)

    # ---- Evidence gates ----
    if len(hits) < 2:
        return {
            "decision": "abstain",
            "reason": "not enough evidence (need ≥2 supporting chunks)",
            "answer": "",
            "citations": []
        }

    max_support = max(h.get("support", 0.0) for h in hits)
    if max_support < 0.20:
        # Treat chit-chat or off-domain questions as no-evidence
        return {
            "decision": "abstain",
            "reason": f"low retrieval support (max_support={max_support:.2f}); ask about content in your documents.",
            "answer": "",
            "citations": []
        }

    # ---- Prompt with a strict citation requirement ----
    ctx = "\n\n".join([f"[{i+1}] {h['text']}" for i,h in enumerate(hits)])
    prompt = f"""You are a careful assistant. Answer ONLY using the facts in the CONTEXT.
Every factual sentence MUST include a citation like [1] or [2] that refers to the numbered context chunks.
If the answer is not present in the context, reply exactly: I don't know based on the provided context.

QUESTION: {q}

CONTEXT:
{ctx}

Return only the final answer with citations, no preface.
"""
    answer = llm.generate(prompt)

    # ---- Post-generation enforcement: must have at least one [n] citation ----
    if not re.search(r"\[\d+\]", answer):
        return {
            "decision": "abstain",
            "reason": "model returned an answer without citations; treating as unsupported",
            "answer": "",
            "citations": []
        }
    contexts = [h["text"] for h in hits]
    if not is_faithful(answer, contexts, thresh=0.55):
        return {
            "decision": "abstain",
            "reason": "low faithfulness to retrieved context (NLI gate)",
            "answer": "",
            "citations": []
        }
    cites = [h['id'] for h in hits]
    verdict = simple_judge(answer)
    return {"decision": "answer", "answer": answer, "citations": cites, "judge": verdict}
