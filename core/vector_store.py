"""Persistent ChromaDB vector store utilities optimized for low memory."""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Any

import chromadb
from chromadb.config import Settings

from core.embeddings import embed_texts
from utils.deduplicator import stable_job_hash

logger = logging.getLogger(__name__)

DEFAULT_PATH = os.getenv("AJM_CHROMA_PATH", "data/chroma_db")
DEFAULT_COLLECTION = os.getenv("AJM_CHROMA_COLLECTION", "jobs")


@dataclass
class JobDocument:
    """Minimal structured job record for vector indexing."""

    job_id: str
    text: str
    metadata: dict[str, Any]


class JobVectorStore:
    """Wrapper around persistent Chroma client with job-centric helpers."""

    def __init__(self, path: str = DEFAULT_PATH, collection_name: str = DEFAULT_COLLECTION) -> None:
        self.client = chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_jobs(self, jobs: list[dict[str, Any]]) -> int:
        """Insert job records with deduplication-aware IDs."""
        if not jobs:
            return 0

        ids: list[str] = []
        docs: list[str] = []
        metas: list[dict[str, Any]] = []

        for job in jobs:
            job_hash = job.get("job_hash") or stable_job_hash(job)
            job_text = "\n".join(
                [
                    job.get("job_title", ""),
                    job.get("company", ""),
                    job.get("description", ""),
                    " ".join(job.get("skills", [])),
                ]
            ).strip()
            if not job_text:
                continue

            ids.append(job_hash)
            docs.append(job_text)
            metas.append(
                {
                    "source_url": job.get("source_url", ""),
                    "company": job.get("company", ""),
                    "source_type": job.get("source_type", "unknown"),
                }
            )

        if not ids:
            return 0

        vectors = embed_texts(docs)
        self.collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)
        logger.info("Upserted %s jobs into vector store", len(ids))
        return len(ids)

    def similarity_search(
        self,
        query_text: str,
        top_k: int = 20,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search similar jobs with optional metadata filters."""
        query_vec = embed_texts([query_text])[0]
        result = self.collection.query(query_embeddings=[query_vec], n_results=top_k, where=where)

        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        rows: list[dict[str, Any]] = []
        for idx, job_id in enumerate(ids):
            rows.append(
                {
                    "job_id": job_id,
                    "document": docs[idx] if idx < len(docs) else "",
                    "metadata": metas[idx] if idx < len(metas) else {},
                    "distance": distances[idx] if idx < len(distances) else None,
                }
            )
        return rows
