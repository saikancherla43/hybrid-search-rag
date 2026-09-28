"""Demo: show how dense, BM25, and hybrid rank chunks differently.

Usage:
    ST_MODEL_DIR=... python demo/demo.py "your question here"

Defaults to an illustrative query where the two rankers genuinely disagree:
"How much does the Growth plan cost per month?" — BM25 nails it on the
literal tokens ("growth", "plan", "cost"); dense embeddings get distracted
by the troubleshooting doc's "Out of build minutes" section (a close
semantic neighbor quoting plan limits). RRF fusion is the tiebreaker.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))
from hybrid import build_retriever  # noqa: E402

DEFAULT_QUERY = "How much does the Growth plan cost per month?"


def main() -> None:
    query = " ".join(sys.argv[1:]) or DEFAULT_QUERY
    retriever = build_retriever()
    print(f"\nQuery: {query}\n")
    for mode in ("dense", "bm25", "hybrid"):
        print(f"=== {mode.upper()} top-3 ===")
        for rank, (chunk, score) in enumerate(retriever.search(query, mode=mode, k=3), start=1):
            snippet = " ".join(chunk.text.split()[:28]) + " ..."
            print(f"  #{rank}  score={score:.4f}  {chunk.doc} > {chunk.section}")
            print(f"       {snippet}")
        print()


if __name__ == "__main__":
    main()
