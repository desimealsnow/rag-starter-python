import re
from typing import List

def split_structured(text: str, max_tokens: int = 500, overlap: int = 50) -> List[str]:
    # very simple tokenization by whitespace (good enough for starter)
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+max_tokens]
        chunks.append(" ".join(chunk))
        i += max_tokens - overlap if max_tokens > overlap else max_tokens
    return chunks
