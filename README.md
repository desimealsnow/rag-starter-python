# RAG Starter (Python) — Ask Questions on Your Docs with Citations

This is a **minimal, production-shaped** Retrieval-Augmented Generation (RAG) service you can run locally in ~10 minutes.

## Features
- **Hybrid retrieval**: dense (Chroma embeddings) + sparse (BM25) with simple fusion
- **Chunking**: structure-aware splitter
- **LLM**: local **Ollama** by default (works offline), or switch to OpenAI via `.env`
- **Hallucination guard**: abstains when support is weak + “answer only from context” prompt
- **API**: FastAPI `POST /ask` → `{ answer, citations[], decision }`
- **Tests**: basic retrieval and evaluation tests
- **Reindex**: `python scripts/bootstrap_index.py` to (re)build your vector store

## Quick Start
1. **Install Python 3.11+** and create a virtual env:
   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install deps**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Install Ollama for local LLM** (no cloud keys needed):
   - macOS/Linux:
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ollama pull llama3.1
     ```
   - Windows: use the official Ollama installer, then run `ollama pull llama3.1`

4. **Add or edit documents** in `data/docs/` (two samples included). Supported: `.txt` (you can add `.md`, basic `.pdf` support later).

5. **Build the index**:
   ```bash
   python scripts/bootstrap_index.py
   ```

6. **Run the API**:
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Try a query**:
   ```bash
   curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "What is the renewal grace period?"}' | jq
   ```

## Switch to OpenAI (optional)
- Copy `.env.example` to `.env` and set:
  ```
  PROVIDER=openai
  OPENAI_API_KEY=sk-...
  OPENAI_MODEL=gpt-4o-mini
  ```

## Project Structure
```
rag-starter-python/
  app/
    __init__.py
    main.py             # FastAPI API
    config.py           # env config
    rag/
      __init__.py
      chunker.py        # structure-aware splitter
      store.py          # Chroma vector store (persistent)
      retriever.py      # Hybrid retrieval + BM25 fusion
      llm.py            # Ollama (default) or OpenAI
      evaluator.py      # simple groundedness/clarity judge
  data/
    docs/               # put your .txt/.md docs here
    index/              # chroma persistence dir
  scripts/
    bootstrap_index.py  # build/rebuild the index
  tests/
    test_retrieval.py
    test_eval.py
  requirements.txt
  .env.example
  README.md
```

## Notes
- This is intentionally lean and readable. When ready, you can add: re-ranker, JSON schema validation, NLI checks, and a Postgres/pgvector store.
- If you prefer Java later, mirror these layers in Spring Boot (DocumentService, VectorStore, RagService, Controller).

Enjoy building! 🚀
