"""Build or rebuild the Chroma index from files in data/docs."""
import os, glob, re
from unidecode import unidecode
from app.config import settings
from app.rag.chunker import split_structured
from app.rag.store import VectorStore

DOCS_DIR = settings.DOCS_DIR

def clean(text: str) -> str:
    t = unidecode(text)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def main():
    files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.txt"))) + sorted(glob.glob(os.path.join(DOCS_DIR, "*.md")))
    if not files:
        print(f"No docs found in {DOCS_DIR}. Add .txt/.md files and rerun.")
        return
    store = VectorStore(settings.INDEX_DIR)
    ids, chunks = [], []
    for fp in files:
        raw = open(fp, "r", encoding="utf-8").read()
        txt = clean(raw)
        pieces = split_structured(txt, max_tokens=400, overlap=60)
        base = os.path.basename(fp)
        for j, p in enumerate(pieces):
            ids.append(f"{base}#{j}")
            chunks.append(p)
    # Reset the collection by recreating client (chromadb PersistentClient collection add() appends)
    # For a fresh build, we can drop and recreate by resetting the client path or collection name versioning.
    # Simpler starter approach: make a new collection by toggling path (not ideal for prod).
    store.add(ids=ids, texts=chunks, metadatas=[{"source": i} for i in ids])
    print(f"Indexed {len(chunks)} chunks from {len(files)} files.")

if __name__ == "__main__":
    main()
