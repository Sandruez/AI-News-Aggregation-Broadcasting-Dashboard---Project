"""
Deduplication pipeline.

Strategy (layered, cheapest first):
  1. Exact URL match — skip if URL already in DB.
  2. Content hash match — skip if title+url hash already stored.
  3. Jaccard similarity on title tokens — if > 0.7, mark duplicate.
  4. Groq LLM semantic check — only for borderline pairs (0.4–0.7 Jaccard).

Precision target: ≥ 0.9 (per BRD).
"""

import re
import logging
from typing import Optional
from groq_service import groq_service

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set[str]:
    stopwords = {"a", "an", "the", "in", "on", "at", "to", "of", "and", "or", "is",
                 "are", "was", "were", "for", "with", "that", "this", "it", "its"}
    tokens = re.findall(r'\b[a-z0-9]+\b', text.lower())
    return {t for t in tokens if len(t) > 2 and t not in stopwords}


def jaccard(a: str, b: str) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


async def is_duplicate(
    title: str,
    content_hash: str,
    existing_hashes: set[str],
    existing_titles: list[str],
) -> tuple[bool, Optional[str]]:
    """
    Returns (is_dup, reason).
    existing_hashes: set of hashes already in DB.
    existing_titles: recent titles to compare against (last ~200).
    """

    # Layer 1 — exact hash
    if content_hash in existing_hashes:
        return True, "exact_hash"

    # Layer 2 — Jaccard similarity
    for existing in existing_titles:
        score = jaccard(title, existing)
        if score >= 0.70:
            return True, f"jaccard_{score:.2f}"
        if 0.40 <= score < 0.70:
            # Layer 3 — LLM semantic check for borderline cases
            try:
                result = await groq_service.are_duplicates(title, existing)
                if result:
                    return True, "llm_semantic"
            except Exception as e:
                logger.warning("LLM dedup failed: %s", e)

    return False, None
