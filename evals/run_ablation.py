"""Ablation: dense-only vs BM25-only vs hybrid (RRF) on the hand-labeled eval set.

Runs all three retrieval modes over the same 10 questions and writes
``results.json`` with recall@3 and MRR per mode, plus per-question detail.

Metrics:
- recall@k: 1.0 if any of the top-k chunks comes from a relevant doc.
- MRR: mean of 1/rank of the first chunk from a relevant doc.

Every number in results.json is measured by this script — no estimates.
Run:  ST_MODEL_DIR=... python evals/run_ablation.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))
from hybrid import build_retriever  # noqa: E402

HERE = Path(__file__).parent
K = 3
MODES = ("dense", "bm25", "hybrid")


def evaluate(retriever, questions: list[dict], mode: str, k: int = K) -> dict:
    per_q = []
    for item in questions:
        q = item["question"]
        relevant = set(item["relevant_docs"])
        ranked = retriever.search(q, mode=mode, k=k)
        docs = [c.doc for c, _ in ranked]
        hit_ranks = [i + 1 for i, d in enumerate(docs) if d in relevant]
        per_q.append({
            "question": q,
            "relevant_docs": sorted(relevant),
            "retrieved_docs": docs,
            "recall@3": 1.0 if hit_ranks else 0.0,
            "reciprocal_rank": 1.0 / hit_ranks[0] if hit_ranks else 0.0,
        })
    n = len(per_q)
    return {
        "mode": mode,
        "k": k,
        "n_questions": n,
        "recall@3": round(sum(p["recall@3"] for p in per_q) / n, 4),
        "mrr": round(sum(p["reciprocal_rank"] for p in per_q) / n, 4),
        "questions": per_q,
    }


def main() -> None:
    questions = json.loads((HERE / "eval_set.json").read_text(encoding="utf-8"))
    retriever = build_retriever()
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dense_backend": retriever.dense_index.backend,
        "bm25": {"k1": retriever.bm25_index.k1, "b": retriever.bm25_index.b},
        "rrf_k": 60,
        "modes": {},
    }
    for mode in MODES:
        print(f"[ablation] running mode={mode} ...")
        results["modes"][mode] = evaluate(retriever, questions, mode)
        m = results["modes"][mode]
        print(f"  recall@3={m['recall@3']:.2f}  mrr={m['mrr']:.2f}")
    out = HERE / "results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"[ablation] wrote {out}")


if __name__ == "__main__":
    main()
