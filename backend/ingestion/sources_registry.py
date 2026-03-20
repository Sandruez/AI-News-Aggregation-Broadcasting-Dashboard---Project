"""
Central registry of all AI news sources.
Add or remove sources here — no changes needed elsewhere.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SourceConfig:
    name: str
    url: str
    feed_url: Optional[str]
    source_type: str  # rss | hn | reddit | arxiv | producthunt
    category: str
    active: bool = True


ALL_SOURCES: list[SourceConfig] = [
    SourceConfig("OpenAI Blog", "https://openai.com/blog", "https://openai.com/blog/rss.xml", "rss", "lab"),
    SourceConfig("Google AI Blog", "https://blog.google/technology/ai/", "https://blog.google/technology/ai/rss/", "rss", "lab"),
    SourceConfig("Meta AI", "https://ai.meta.com/blog/", "https://ai.meta.com/blog/rss/", "rss", "lab"),
    SourceConfig("Anthropic", "https://www.anthropic.com/news", "https://www.anthropic.com/rss.xml", "rss", "lab"),
    SourceConfig("DeepMind", "https://deepmind.google/discover/blog/", "https://deepmind.google/blog/rss.xml", "rss", "lab"),
    SourceConfig("Hugging Face Blog", "https://huggingface.co/blog", "https://huggingface.co/blog/feed.xml", "rss", "community"),
    SourceConfig("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/", "https://techcrunch.com/category/artificial-intelligence/feed/", "rss", "media"),
    SourceConfig("VentureBeat AI", "https://venturebeat.com/ai/", "https://venturebeat.com/category/ai/feed/", "rss", "media"),
    SourceConfig("The Verge Tech", "https://www.theverge.com/ai-artificial-intelligence", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "rss", "media"),
    SourceConfig("Wired AI", "https://www.wired.com/tag/artificial-intelligence/", "https://www.wired.com/feed/tag/ai/latest/rss", "rss", "media"),
    SourceConfig("MIT Tech Review", "https://www.technologyreview.com/topic/artificial-intelligence/", "https://www.technologyreview.com/topic/artificial-intelligence/feed", "rss", "media"),
    SourceConfig("Microsoft AI Blog", "https://blogs.microsoft.com/ai/", "https://blogs.microsoft.com/ai/feed/", "rss", "lab"),
    SourceConfig("Stability AI Blog", "https://stability.ai/blog", "https://stability.ai/blog/rss.xml", "rss", "lab"),
    SourceConfig("Y Combinator Blog", "https://www.ycombinator.com/blog", "https://www.ycombinator.com/blog/rss", "rss", "vc"),
    SourceConfig("arXiv cs.AI", "https://arxiv.org/list/cs.AI/recent", None, "arxiv", "research"),
    SourceConfig("arXiv cs.LG", "https://arxiv.org/list/cs.LG/recent", None, "arxiv", "research"),
    SourceConfig("PapersWithCode", "https://paperswithcode.com", "https://paperswithcode.com/rss", "rss", "research"),
    SourceConfig("Hacker News AI", "https://news.ycombinator.com", None, "hn", "community"),
    SourceConfig("Reddit r/MachineLearning", "https://www.reddit.com/r/MachineLearning/", "https://www.reddit.com/r/MachineLearning/.rss", "rss", "community"),
    SourceConfig("Product Hunt AI", "https://www.producthunt.com/topics/artificial-intelligence", None, "producthunt", "products"),
]
