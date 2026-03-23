"""
Ingestion package for AI News Dashboard
Handles RSS fetching, deduplication, AI enrichment, and persistence.
"""

from .scheduler import start_scheduler
from .fetcher import fetch_rss, fetch_hacker_news, fetch_arxiv
from .deduplicator import is_duplicate
from .sources_registry import ALL_SOURCES

__all__ = [
    'start_scheduler',
    'fetch_rss', 
    'fetch_hacker_news', 
    'fetch_arxiv',
    'is_duplicate',
    'ALL_SOURCES'
]