# RAG Starter — Technical README (Current state + ongoing changes)

**Goal:** a minimal, production-shaped RAG service: *retrieve → assemble context → generate answer with citations → enforce guardrails*. This is an **ongoing document**. Append changes to the Changelog and Roadmap below.

---

## Architecture (v0.1.1)
```
data/docs  ──►  Ingest/Clean/Chunk  ──►  VectorStore (Chroma) + BM25 corpus
                                               │
                                               ▼
                                   HybridRetriever (dense + sparse, fusion)
                                               │ (k=6; optional reranker soon)
                                               ▼
                               Context Builder (token-budgeted, numbered chunks)
                                               │
                                               ▼
                          LLM Client (Groq/OpenAI/Ollama; temperature=0)
                                               │
                                               ▼
                  Post-Gen Enforcement (citations required; abstain if missing)
                                               │
                                               ▼
                       Evaluator (toy G-Eval: groundedness/clarity/completeness)
                                               │
                                               ▼
                                   FastAPI `/ask` JSON response
```

**Key properties**
- **Evidence-first**: must cite `[n]` for claims or we abstain.
- **Abstention gates**: (a) ≥2 chunks required, (b) lexical support threshold.
- **Pluggable LLM provider** via `.env` (`groq`, `openai`, or `ollama`).

---

## Repo Layout
```
app/
  main.py              # API + guardrails + citation enforcement
  config.py            # env & settings
  rag/
    chunker.py         # naive chunking (window+overlap)
    store.py           # Chroma persistent client (data/index)
    retriever.py       # hybrid retrieval + (optional) reranker hook
    llm.py             # providers: groq, openai, ollama
    evaluator.py       # toy G-Eval
data/
  docs/                # your source files (.txt/.md for now)
  index/               # Chroma persistence
scripts/
  bootstrap_index.py   # (re)builds the index from data/docs
tests/
  test_retrieval.py
  test_eval.py
  test_safety.py       # hello-abstain smoke
```

---

## Environment & Providers
Create `.env` in project root (see `.env.example`). Examples:

### Groq (current)
```
PROVIDER=groq
GROQ_API_KEY=sk_...
GROQ_MODEL=llama-3.1-8b-instant
```

### OpenAI
```
PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Ollama (local)
```
PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

**Run with env loaded**
- `uvicorn app.main:app --reload` (if `dotenv.load_dotenv()` is in `llm.py`), or  
- `uvicorn app.main:app --reload --env-file .env`, or  
- VS Code launch config with `"envFile": "${workspaceFolder}/.env"`.

---

## Commands
```bash
# (once) create venv and install
python -m venv .venv && . .venv/Scripts/activate    # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pydantic-settings>=2.4.0

# index docs
python -m scripts.bootstrap_index

# run api
uvicorn app.main:app --reload

# test
pytest -q
```

---

## API Contract
**POST `/ask`**
```json
{ "question": "What is the renewal grace period?" }
```
**Response**
```json
{
  "decision": "answer",
  "answer": "Customers typically have 30 days after expiry... [1]",
  "citations": ["policy.txt#0", "faq.txt#0"],
  "judge": { "scores": { "grounded": 5, "completeness": 4, "clarity": 5 }, "verdict": "pass" }
}
```
Abstention example:
```json
{
  "decision": "abstain",
  "reason": "low retrieval support (max_support=0.12)"
}
```

---

## Retrieval Details (current)
- **Dense**: Chroma’s default embedding pipeline for `documents`/`query_texts`.  
- **Sparse**: BM25 over the same chunks.
- **Fusion**: simple union, keep first-seen up to `k`.
- **Support score**: lexical overlap (`_lex_overlap`) for quick gating.
- **Gates**: `len(hits) >= 2` and `max_support >= 0.20`.

> Optional **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (CPU OK) to re-order top candidates. See `retriever.py` hook.

---

## Guardrails & Evaluation
- **Citations required**: regex check `\[\d+\]` or abstain.
- **“Only from context”** prompt; temperature 0.
- **Toy G-Eval**: groundedness, completeness, clarity → `"pass"`/`"needs-review"`.

**Next guardrail (optional)**
- **Faithfulness NLI gate**: `cross-encoder/nli-deberta-v3-base` → abstain if no context chunk entails each answer sentence.

---

## Known Limitations
- Chroma default embeddings are fine for a starter, not optimal for domain heavy text.  
- Chunking is whitespace-based; structure-aware chunking for PDFs/emails is a future task.  
- No persistence for Q/A logs or analytics yet.  
- No rate limiting or auth on the API.

---

## Roadmap (living)
- [ ] Add reranker (MiniLM cross-encoder) and bump precision@k.
- [ ] Add NLI faithfulness gate; configurable threshold.
- [ ] Semantic cache (Redis) for repeated queries.
- [ ] Move vectors to **pgvector** or **Qdrant**; keep BM25 via OpenSearch.
- [ ] Add exact span citations (start/end offsets) and highlight in UI.
- [ ] Web UI (Next.js) with side-by-side evidence viewer.
- [ ] Add LoRA/QLoRA fine-tuning pipeline for style/format control.
- [ ] Observability: request logs, error taxonomy, dashboard.
- [ ] Deployment: Dockerfile + Compose (LLM provider via env), optional Nginx.
- [ ] Security: API key auth, rate limit, CORS policy.

---

## Changelog
**v0.1.1**
- Load `.env` reliably; added safe debug prints for provider + key presence.
- Added **evidence gates**: min 2 hits, lexical support threshold.
- Enforced **citations**; abstain if missing.
- Added `test_safety.py` (hello-abstain smoke).

**v0.1.0**
- Initial scaffold: ingestion, Chroma store, BM25, FastAPI `/ask`, toy judge, sample docs.


