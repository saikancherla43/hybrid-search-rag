"""Hybrid retrieval: Reciprocal Rank Fusion (RRF) of BM25 + dense rankings.

Why fusion instead of score blending: BM25 scores and cosine similarities
live on incomparable scales, and normalizing them is brittle. RRF fuses
*rankings*, not scores:

    RRF_score(chunk) = sum over rankings r of  1 / (k_rrf + rank_r(chunk))

with k_rrf=60 (the standard constant from Cormack et al., SIGIR 2009).
A chunk that both rankers place highly gets a large boost; a chunk ranked
highly by only one ranker still contributes. No tuning, no score
normalization, deterministic.

Modes:
- "dense"  — dense embeddings only (the baseline most RAG demos ship)
- "bm25"   — keyword search only (the baseline most docs sites ship)
- "hybrid" — RRF fusion of both
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).parent))

from bm25 import BM25Index  # noqa: E402
from embed import DenseIndex  # noqa: E402
from ingest import Chunk, ingest  # noqa: E402

if TYPE_CHECKING:
    pass

RRF_K = 60  # standard RRF constant


def rrf_fuse(ranked_lists: list[list[tuple[Chunk, float]]],
             k: int = RRF_K) -> list[tuple[Chunk, float]]:
    """Fuse full rankings (best-first (chunk, score) lists) via RRF."""
    fused: dict[str, float] = {}
    by_id: dict[str, Chunk] = {}
    for ranked in ranked_lists:
        for rank, (chunk, _score) in enumerate(ranked, start=1):
            by_id[chunk.id] = chunk
            fused[chunk.id] = fused.get(chunk.id, 0.0) + 1.0 / (k + rank)
    return sorted(((by_id[cid], s) for cid, s in fused.items()),
                  key=lambda t: t[1], reverse=True)


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], dense_index: DenseIndex):
        self.chunks = chunks
        self.dense_index = dense_index
        self.bm25_index = BM25Index(chunks)

    def search(self, query: str, mode: str = "hybrid", k: int = 3,
               rrf_k: int = RRF_K) -> list[tuple[Chunk, float]]:
        """Top-k (chunk, score) in the requested mode. Hybrid scores are RRF
        fusion scores; single-mode scores are that mode's native scores."""
        if mode == "dense":
            return self.dense_index.rank(query, k=k)
        if mode == "bm25":
            return self.bm25_index.rank(query, k=k)
        if mode == "hybrid":
            fused = rrf_fuse(
                [self.dense_index.rank(query), self.bm25_index.rank(query)],
                k=rrf_k,
            )
            return fused[:k]
        raise ValueError(f"unknown mode {mode!r}; expected dense/bm25/hybrid")


def build_retriever(corpus_dir: str | Path | None = None) -> HybridRetriever:
    corpus_dir = Path(corpus_dir) if corpus_dir else Path(__file__).parent.parent / "corpus"
    chunks = ingest(corpus_dir)
    print(f"[hybrid] building dense index over {len(chunks)} chunks ...")
    from embed import build_index

    dense = build_index(chunks)
    print(f"[hybrid] dense backend: {dense.backend}")
    return HybridRetriever(chunks, dense)


if __name__ == "__main__":
    import os

    os.environ.setdefault(
        "ST_MODEL_DIR",
        str(Path(__file__).parent.parent.parent / "rag-demo" / "models" / "all-MiniLM-L6-v2"),
    )
    r = build_retriever()
    q = "how much does the growth plan cost?"
    for mode in ("dense", "bm25", "hybrid"):
        print(f"--- {mode} ---")
        for chunk, score in r.search(q, mode=mode, k=3):
            print(f"  {score:.4f}  {chunk.id} [{chunk.section}]")
