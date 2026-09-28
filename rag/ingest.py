"""Ingestion: load markdown docs from corpus/ and split into overlapping chunks.

Chunking strategy: split each document on level-2 headings (``##``), then
pack sections into chunks of ~MAX_WORDS words with OVERLAP_WORDS of overlap
between consecutive chunks. Chunk ids are deterministic so eval labels can
reference documents by filename stem.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MAX_WORDS = 300      # ~400 tokens
OVERLAP_WORDS = 40


@dataclass
class Chunk:
    id: str
    doc: str          # filename stem, e.g. "pricing-plans"
    title: str        # document title (first # heading)
    section: str      # section heading this chunk belongs to
    text: str


def _split_sections(md: str) -> tuple[str, list[tuple[str, str]]]:
    """Split markdown into (title, [(section_heading, body)]) on '## ' headings."""
    parts = re.split(r"(?m)^##\s+", md)
    intro = parts[0].strip()
    sections: list[tuple[str, str]] = []
    title_match = re.search(r"(?m)^#\s+(.+)$", intro)
    title = title_match.group(1).strip() if title_match else "Untitled"
    if (intro_body := re.sub(r"(?m)^#\s+.+$", "", intro).strip()):
        sections.append(("Overview", intro_body))
    for part in parts[1:]:
        lines = part.splitlines()
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        sections.append((heading, body))
    return title, sections


def _chunk_words(words: list[str]) -> list[list[str]]:
    chunks, start = [], 0
    while start < len(words):
        end = min(start + MAX_WORDS, len(words))
        chunks.append(words[start:end])
        if end == len(words):
            break
        start = end - OVERLAP_WORDS
    return chunks


def ingest(corpus_dir: str | Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for md_file in sorted(Path(corpus_dir).glob("*.md")):
        md = md_file.read_text(encoding="utf-8")
        doc = md_file.stem
        title, sections = _split_sections(md)
        for s_idx, (heading, body) in enumerate(sections):
            words = body.split()
            if not words:
                continue
            for c_idx, wc in enumerate(_chunk_words(words)):
                chunks.append(
                    Chunk(
                        id=f"{doc}::s{s_idx}::c{c_idx}",
                        doc=doc,
                        title=title,
                        section=heading,
                        text=" ".join(wc),
                    )
                )
    return chunks


if __name__ == "__main__":
    cs = ingest(Path(__file__).parent.parent / "corpus")
    print(f"{len(cs)} chunks from corpus/")
    for c in cs[:3]:
        print(f"  {c.id} [{c.section}] ({len(c.text.split())} words)")
