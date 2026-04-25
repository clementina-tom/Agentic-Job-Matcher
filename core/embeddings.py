"""Low-memory embedding manager with caching and optional quantization."""

from __future__ import annotations

import hashlib
import logging
import os
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = os.getenv("AJM_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CACHE_DIR = Path(os.getenv("AJM_EMBED_CACHE_DIR", "data/cache/embeddings"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_MODEL_LOCK = Lock()


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """Return a singleton sentence-transformers model instance."""
    with _MODEL_LOCK:
        logger.info("Loading embedding model: %s", model_name)
        model = SentenceTransformer(model_name)
        return model


def _cache_key(text: str, model_name: str, quantize_bits: int) -> str:
    seed = f"{model_name}|{quantize_bits}|{text}".encode("utf-8")
    return hashlib.sha1(seed).hexdigest()


def _quantize(arr: np.ndarray, bits: int = 8) -> np.ndarray:
    """Quantize vector for lower-memory storage and faster I/O."""
    if bits == 8:
        scale = np.max(np.abs(arr)) or 1.0
        quantized = (arr / scale * 127.0).astype(np.int8)
        restored = (quantized.astype(np.float32) * scale) / 127.0
        return restored
    return arr.astype(np.float32)


def embed_texts(
    texts: Iterable[str],
    model_name: str = DEFAULT_MODEL_NAME,
    quantize_bits: int = 8,
    use_disk_cache: bool = True,
) -> list[list[float]]:
    """Embed text values with optional disk caching and quantization.

    Caching reduces repeated work across runs.
    """
    model = get_embedding_model(model_name)
    results: list[list[float]] = []

    for text in texts:
        key = _cache_key(text, model_name, quantize_bits)
        cache_file = CACHE_DIR / f"{key}.npy"

        if use_disk_cache and cache_file.exists():
            vec = np.load(cache_file)
            results.append(vec.tolist())
            continue

        vec = model.encode(text, normalize_embeddings=True)
        vec_array = np.asarray(vec, dtype=np.float32)
        vec_array = _quantize(vec_array, bits=quantize_bits)

        if use_disk_cache:
            np.save(cache_file, vec_array)

        results.append(vec_array.tolist())

    return results
