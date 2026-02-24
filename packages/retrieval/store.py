from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from packages.core.config import get_settings
from packages.retrieval.chunking import chunk_text


@dataclass
class RetrievedDoc:
    source_id: str
    text: str
    score: float


class RetrievalBackend:
    def index_corpus(self) -> int:
        raise NotImplementedError

    def retrieve(self, query: str, top_k: int) -> list[RetrievedDoc]:
        raise NotImplementedError


class InMemoryRetrievalBackend(RetrievalBackend):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.docs: list[RetrievedDoc] = []

    def index_corpus(self) -> int:
        corpus_dir = Path(self.settings.corpus_path)
        files = list(corpus_dir.glob("*.md")) + list(corpus_dir.glob("*.txt"))
        docs: list[RetrievedDoc] = []
        for file in files:
            text = file.read_text(encoding="utf-8")
            chunks = chunk_text(
                file.stem,
                text,
                self.settings.chunk_size,
                self.settings.chunk_overlap,
            )
            docs.extend(RetrievedDoc(source_id=c.source_id, text=c.text, score=0.0) for c in chunks)
        self.docs = docs
        return len(docs)

    def retrieve(self, query: str, top_k: int) -> list[RetrievedDoc]:
        if not self.docs:
            self.index_corpus()
        q = set(query.lower().split())
        scored: list[RetrievedDoc] = []
        for d in self.docs:
            overlap = len(q & set(d.text.lower().split()))
            scored.append(RetrievedDoc(source_id=d.source_id, text=d.text, score=float(overlap)))
        return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]


class ChromaRetrievalBackend(InMemoryRetrievalBackend):
    def __init__(self) -> None:
        super().__init__()
        import chromadb
        from chromadb.utils import embedding_functions

        self.client = chromadb.PersistentClient(path=self.settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="careweave_corpus",
            embedding_function=cast(Any, embedding_functions.DefaultEmbeddingFunction()),
        )

    def index_corpus(self) -> int:
        corpus_dir = Path(self.settings.corpus_path)
        files = list(corpus_dir.glob("*.md")) + list(corpus_dir.glob("*.txt"))
        total = 0
        existing = self.collection.get(include=[])
        if existing.get("ids"):
            self.collection.delete(ids=existing["ids"])
        for file in files:
            text = file.read_text(encoding="utf-8")
            chunks = chunk_text(
                file.stem,
                text,
                self.settings.chunk_size,
                self.settings.chunk_overlap,
            )
            if not chunks:
                continue
            ids = [f"{file.stem}-{i}" for i in range(len(chunks))]
            docs = [chunk.text for chunk in chunks]
            metas: list[Mapping[str, Any]] = [
                {"source_id": chunk.source_id} for chunk in chunks
            ]
            self.collection.add(ids=ids, documents=docs, metadatas=metas)
            total += len(chunks)
        return total

    def retrieve(self, query: str, top_k: int) -> list[RetrievedDoc]:
        result = self.collection.query(query_texts=[query], n_results=top_k)
        docs: list[RetrievedDoc] = []

        documents = cast(list[list[str]], result.get("documents") or [[]])
        metadatas = cast(
            list[list[Mapping[str, Any]]],
            result.get("metadatas") or [[]],
        )
        distances = cast(list[list[float]], result.get("distances") or [[]])

        docs_batch = documents[0] if documents else []
        metas_batch = metadatas[0] if metadatas else []
        distances_batch = distances[0] if distances else []

        for doc, meta, distance in zip(docs_batch, metas_batch, distances_batch):
            docs.append(
                RetrievedDoc(
                    source_id=str(meta.get("source_id", "unknown")),
                    text=doc,
                    score=1 - float(distance),
                )
            )
        return docs


def default_backend() -> RetrievalBackend:
    try:
        return ChromaRetrievalBackend()
    except Exception:
        return InMemoryRetrievalBackend()
