import re
from typing import List
import numpy as np

try:
    from sentence_transformers import CrossEncoder
    _NLI_AVAILABLE = True
except Exception as _e:
    print("[NLI] sentence-transformers not available:", _e)
    _NLI_AVAILABLE = False

_MODEL_NAME = "cross-encoder/nli-deberta-v3-base"
_model = None

def _lazy_model():
    global _model
    if not _NLI_AVAILABLE:
        return None
    if _model is None:
        try:
            _model = CrossEncoder(_MODEL_NAME, device="cpu")
            print("[NLI] loaded", _MODEL_NAME)
        except Exception as e:
            print("[NLI] disabled:", e)
            return None
    return _model

def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]

def _softmax(x: np.ndarray, axis=-1) -> np.ndarray:
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)

def is_faithful(answer: str, contexts: List[str], thresh: float = 0.55) -> bool:
    """
    For each answer sentence, require at least one context chunk that 'entails' it.
    Works with CrossEncoder outputs that are either:
    - 1D scores (regression style), OR
    - 2D logits with 3 classes [contradiction, neutral, entailment].
    """
    model = _lazy_model()
    if model is None:
        # If NLI model missing, don't block; treat as faithful.
        return True

    sents = split_sentences(answer)
    if not sents or not contexts:
        return False

    for s in sents:
        # strip inline citation tokens like [1]
        s_clean = re.sub(r"\[\d+\]", "", s).strip()
        if not s_clean:
            continue

        pairs = [(ctx, s_clean) for ctx in contexts]
        raw = model.predict(pairs)  # shape: (N,) or (N,3)

        scores = np.asarray(raw)
        if scores.ndim == 1:
            # Single score per pair (higher = better)
            entail_scores = scores
            max_entail = float(np.max(entail_scores))
        else:
            # 3-class logits -> convert to probs, take entailment column (index 2)
            # Convention for this model family: [contradiction, neutral, entailment]
            probs = _softmax(scores, axis=1)
            entail_probs = probs[:, 2]
            max_entail = float(np.max(entail_probs))

        if max_entail < thresh:
            return False

    return True
