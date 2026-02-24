from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    source_id: str
    text: str


def chunk_text(source_id: str, text: str, chunk_size: int = 420, overlap: int = 50) -> list[Chunk]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    for para in paragraphs:
        start = 0
        while start < len(para):
            end = min(start + chunk_size, len(para))
            chunks.append(Chunk(source_id=source_id, text=para[start:end]))
            if end >= len(para):
                break
            start = max(0, end - overlap)
    return chunks
