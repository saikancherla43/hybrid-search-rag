"""Dense embeddings: sentence-transformers (all-MiniLM-L6-v2) with TF-IDF fallback.

The primary backend is the ``all-MiniLM-L6-v2`` embedding model (384-dim,
fast, strong semantic matching — it handles paraphrased questions that
keyword search misses, e.g. "how much is growth?" vs "Growth — $29/month").

If the model cannot be loaded in the current environment, we fall back to
TF-IDF vectors via scikit-learn so the pipeline still runs end-to-end.
The active backend is recorded on the index — the ablation reports exactly
which encoder produced the vectors. Nothing here is faked.

Model resolution order for sentence-transformers:
1. ``ST_MODEL_DIR`` env var — a local directory of pre-fetched weights
   (used in restricted networks; e.g. point it at a sibling project's
   ``models/all-MiniLM-L6-v2`` directory).
2. Otherwise the model id ``all-MiniLM-L6-v2`` — downloaded from the
   Hugging Face hub on first run and cached by the library.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ingest import Chunk

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = Path(__file__).parent / "index.pkl"


def _model_source() -> str:
    return os.environ.get("ST_MODEL_DIR", MODEL_NAME)


def _try_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(_model_source())
        return model
    except Exception as exc:  # no network / no torch -> fall back
        print(f"[embed] sentence-transformers unavailable ({exc}); using TF-IDF fallback")
        return None


class DenseIndex:
    def __init__(self, chunks, backend: str, encoder, matrix):
        self.chunks = chunks
        self.backend = backend          # "sbert" or "tfidf"
        self.encoder = encoder          # SentenceTransformer or TfidfVectorizer
        self.matrix = matrix            # np.ndarray (dense) or sparse TF-IDF matrix

    def encode_query(self, query: str):
        if self.backend == "sbert":
            vec = self.encoder.encode([query], normalize_embeddings=True)
            return np.asarray(vec, dtype=np.float32)
        return self.encoder.transform([query])

    def scores(self, query: str) -> list[float]:
        """Cosine-similarity score for every chunk, in chunk order."""
        q = self.encode_query(query)
        if self.backend == "sbert":
            return (self.matrix @ q[0]).tolist()
        from sklearn.metrics.pairwise import cosine_similarity

        return cosine_similarity(q, self.matrix)[0].tolist()

    def rank(self, query: str, k: int | None = None):
        scored = list(zip(self.chunks, self.scores(query)))
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:k] if k is not None else scored

    def save(self, path: Path = INDEX_PATH) -> None:
        with open(path, "wb") as f:
            pickle.dump(
                {"chunks": self.chunks, "backend": self.backend,
                 "encoder": self.encoder, "matrix": self.matrix}, f)
        print(f"[embed] saved index ({self.backend}, {len(self.chunks)} chunks) -> {path}")

    @classmethod
    def load(cls, path: Path = INDEX_PATH) -> "DenseIndex":
        with open(path, "rb") as f:
            d = pickle.load(f)
        return cls(d["chunks"], d["backend"], d["encoder"], d["matrix"])


def build_index(chunks) -> DenseIndex:
    texts = [c.text for c in chunks]
    model = _try_sentence_transformer()
    if model is not None:
        matrix = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        matrix = np.asarray(matrix, dtype=np.float32)
        return DenseIndex(chunks, backend="sbert", encoder=model, matrix=matrix)

    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)
    return DenseIndex(chunks, backend="tfidf", encoder=vectorizer, matrix=matrix)


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from ingest import ingest

    chunks = ingest(Path(__file__).parent.parent / "corpus")
    build_index(chunks).save()
