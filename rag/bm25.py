"""BM25 ranking over chunk text — implemented from scratch, stdlib only.

This is the keyword side of the hybrid retriever. BM25 scores exact term
overlap with length normalization and IDF weighting, which is exactly what
dense embeddings are weak at: order IDs, error codes, plan names, and other
rare literal tokens.

Standard formulation (k1=1.5, b=0.75):

    score(q, d) = sum over query terms t of
        IDF(t) * (tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl))

IDF uses the Robertson/Sparck-Jones form with a +1 floor so terms appearing
in every document still contribute a small positive weight instead of going
negative.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ingest import Chunk

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    """Precomputed BM25 statistics for a fixed chunk list."""

    def __init__(self, chunks: "list[Chunk]", k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.N = len(chunks)
        self.doc_tokens = [tokenize(c.text) for c in chunks]
        self.doc_lens = [len(t) for t in self.doc_tokens]
        self.avgdl = sum(self.doc_lens) / self.N if self.N else 0.0
        self.tf: list[Counter] = [Counter(t) for t in self.doc_tokens]
        df: Counter = Counter()
        for toks in self.doc_tokens:
            for term in set(toks):
                df[term] += 1
        self.df = df

    def _idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))

    def scores(self, query: str) -> list[float]:
        """BM25 score for every chunk, in chunk order."""
        qterms = tokenize(query)
        out: list[float] = []
        for i in range(self.N):
            dl = self.doc_lens[i]
            norm = (1 - self.b + self.b * dl / self.avgdl) if self.avgdl else 1.0
            s = 0.0
            for t in qterms:
                tf = self.tf[i].get(t, 0)
                if not tf:
                    continue
                s += self._idf(t) * (tf * (self.k1 + 1)) / (tf + self.k1 * norm)
            out.append(s)
        return out

    def rank(self, query: str, k: int | None = None) -> list[tuple["Chunk", float]]:
        """Full BM25 ranking as (chunk, score) pairs, best first."""
        scored = list(zip(self.chunks, self.scores(query)))
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:k] if k is not None else scored


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from ingest import ingest

    idx = BM25Index(ingest(Path(__file__).parent.parent / "corpus"))
    for chunk, score in idx.rank("how much does the growth plan cost?", k=3):
        print(f"{score:.3f}  {chunk.id} [{chunk.section}]")
