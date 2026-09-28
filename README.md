# Hybrid-Search RAG — BM25 + Dense Embeddings with Reciprocal Rank Fusion

A working hybrid retrieval pipeline over a fictional SaaS help center ("Acme Cloud"),
built as a portfolio case study. It answers the question every RAG tutorial skips:
**what do you actually gain by adding keyword search to dense embeddings?**
The answer here is measured, not asserted — including the places where hybrid
does *not* win.

## The problem

Dense embeddings and keyword search fail in opposite ways:

- **Dense-only** retrieval misses on exact terms. Ask "How much does the Growth
  plan cost?" and the embedding model ranks the troubleshooting doc's
  *"Out of build minutes"* section first — it's a close semantic neighbor
  (it quotes plan minute limits) but it's the wrong section. Literal tokens
  like plan names, error codes, and order IDs get washed out in vector space.
- **BM25-only** misses on paraphrase. Ask "What should I do if my deploy fails
  with a 502 Bad Gateway error?" and keyword overlap alone ranks the right
  troubleshooting doc only 3rd — the query shares few literal terms with the
  answer section.

Production RAG systems fuse both. This project implements that fusion and
measures it honestly.

## What was built

- **Corpus** (`corpus/`): 8 realistic help-center docs (getting started, pricing,
  API auth, webhooks, troubleshooting, security & compliance, billing, integrations),
  chunked on `##` headings into 54 chunks (~300 words, 40-word overlap).
- **Pipeline** (`rag/`):
  - `ingest.py` — deterministic chunking; chunk ids encode doc/section.
  - `bm25.py` — BM25 implemented **from scratch** (stdlib only, ~60 lines:
    k1=1.5, b=0.75, Robertson/Sparck-Jones IDF with a +1 floor).
  - `embed.py` — dense embeddings with `all-MiniLM-L6-v2` (384-dim). In
    restricted networks the weights can be pre-fetched and loaded via the
    `ST_MODEL_DIR` env var; a TF-IDF fallback keeps the pipeline runnable
    anywhere. The active backend is recorded and reported.
  - `hybrid.py` — Reciprocal Rank Fusion (RRF, k=60, the standard constant)
    over the two full rankings, plus pure `dense` and pure `bm25` modes for
    the ablation. RRF fuses *rankings*, not scores — BM25 scores and cosine
    similarities live on incomparable scales, and normalizing them is brittle.
- **Ablation** (`evals/`): the same 10 hand-labeled questions used in the
  dense-only demo, run through all three modes. `run_ablation.py` writes
  `results.json` with recall@3 and MRR per mode. Ground truth is at
  **document level** (the eval labels docs, not chunks) — a documented
  limitation, not a hidden one.
- **Demo** (`demo/demo.py` + `demo/transcript.md`): one query, three rankings,
  side by side.

## Architecture

```
corpus/*.md → ingest (heading chunks, 54 total)
    ├──→ BM25 index (from-scratch, exact-term ranking)
    └──→ dense index (MiniLM-L6-v2, 384-d, cosine)
              │
              ▼
   RRF fusion (k=60):  score = Σ 1/(60 + rank)  per ranker
              │
              ▼
   top-k chunks → (plug in any answer layer)
```

## Ablation results

Measured by `evals/run_ablation.py` on the 10-question hand-labeled set
(dense backend: `all-MiniLM-L6-v2`; BM25 k1=1.5, b=0.75; RRF k=60):

| Mode | recall@3 | MRR |
|---|---|---|
| dense-only | **1.00** | **0.90** |
| bm25-only | 1.00 | 0.83 |
| hybrid (RRF) | 1.00 | 0.83 |

### The honest read

- **All three modes hit recall@3 = 1.00.** On a small, well-written corpus,
  every approach finds the right document in the top 3. Retrieval is not the
  bottleneck here — and a case study that pretends otherwise would be lying.
- **Dense-only wins on MRR (0.90).** I'm reporting that plainly even though
  this project is *about* hybrid search. 7 of 10 questions rank identically
  across all three modes; fusion has little headroom when one ranker is
  already near-ceiling.
- **Where the rankers genuinely disagree** (the interesting 3 questions):
  - *"How much does the Growth plan cost?"* — BM25 ranks the right section
    **#1** on literal tokens ("growth", "plan", "cost"); dense ranks the
    troubleshooting doc first (RR 0.5). RRF produces an **exact tie**
    (both candidates score 1/61 + 1/62), broken by insertion order — so
    hybrid inherits dense's miss (RR 0.5). Fusion with equal weights cannot
    break near-ties; a weighted RRF or score-aware blend would.
  - *"Deploy fails with 502 Bad Gateway"* — dense ranks the troubleshooting
    doc #1; BM25 only #3 (few shared literal terms). Hybrid follows BM25
    *down* (RR 0.33). Fusion is not free: a confidently-wrong ranker drags
    the good one with it.
  - *"How long are deploy logs retained?"* — the reverse: BM25 misses at #2,
    dense is #1, and hybrid **rescues** it back to #1. This is the case
    hybrid exists for.
- **BM25 alone is free.** No model download, no GPU, no embedding infra —
  and it still gets recall@3 = 1.00 here. For small corpora with
  term-heavy queries, it's a legitimate production choice, not just a baseline.

**Takeaway:** hybrid's value on this corpus is *robustness*, not beating a
strong dense ranker. It never ranks worse than the weaker ranker and it
fixed BM25's worst miss — but on a small corpus where dense is already
excellent, dense-only is the right call. Hybrid earns its complexity where
queries mix exact tokens (order IDs, error codes, SKUs) with paraphrase, at
corpus sizes where no single ranker dominates. That's exactly when I'd
recommend it to a client — and exactly what I'd tell them about the tradeoff.

## How to run

```bash
pip install -r requirements.txt

# Dense backend: either let sentence-transformers download the model,
# or point at pre-fetched weights (restricted networks):
export ST_MODEL_DIR=/path/to/models/all-MiniLM-L6-v2

# Run the ablation (writes evals/results.json)
python evals/run_ablation.py

# Compare the three rankings on one query
python demo/demo.py "How much does the Growth plan cost per month?"
```

No API keys needed. Everything runs locally.

## Production notes

- **Weighted RRF or score fusion**: this demo uses equal-weight RRF (k=60).
  In production I'd try per-ranker weights tuned on a larger eval set, or a
  learned blend — the Q1 tie above is the concrete reason.
- **Per-query routing**: route exact-term queries (IDs, codes, quoted phrases)
  toward BM25 weight and paraphrased questions toward dense — a cheap
  classifier on query features, evaluated the same way.
- **Eval at chunk level**: this demo's labels are doc-level, which flatters
  all modes. Chunk-level labels (or an LLM judge on final answers) would
  separate them further.
- **Scale**: at millions of chunks, BM25 runs on an inverted index
  (this from-scratch version is O(corpus) per query — fine for a demo) and
  dense needs ANN (HNSW/IVF). The RRF layer is unchanged.
- **Answer layer**: retrieval is extractive-ready; plug any LLM into a
  `synthesize()` step with citations, as in the companion dense-only demo.

## Tech stack

Python, sentence-transformers (`all-MiniLM-L6-v2`), scikit-learn (TF-IDF
fallback), numpy. BM25 from scratch — no `rank-bm25` dependency.
