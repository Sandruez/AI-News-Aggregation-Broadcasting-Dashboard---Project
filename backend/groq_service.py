"""
Groq LLM service for AI-assisted features:
- Article summarization
- LinkedIn caption generation
- Deduplication via semantic comparison
- Impact scoring
"""

import httpx
import json
import logging
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqService:
    def __init__(self):
        self.base_url = settings.groq_base_url
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _chat(self, messages: list[dict], max_tokens: int = 512) -> str:
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set; skipping LLM call.")
            return ""

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.4,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def summarize(self, title: str, raw_text: str) -> str:
        """
        Produce a concise, plain-English summary of a news article.
        Reads like a human wrote it — no bullet points, no jargon walls.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a skilled tech journalist. Write a 2–3 sentence summary "
                    "of the article below. Be conversational and clear. No bullet points. "
                    "Do not mention 'the article' or 'this piece'. Just the key insight."
                ),
            },
            {
                "role": "user",
                "content": f"Title: {title}\n\n{raw_text[:3000]}",
            },
        ]
        return await self._chat(messages, max_tokens=200)

    async def generate_linkedin_caption(self, title: str, summary: str, url: str) -> str:
        """
        Write a LinkedIn post caption for sharing a news item.
        Engaging, professional, ends with a question or CTA.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You write LinkedIn posts for AI professionals. "
                    "Write a compelling 3–5 sentence post that shares the news, gives your take, "
                    "and ends with an engaging question or call to action. "
                    "Use 1–2 relevant emojis. No hashtag spam. Sound like a human, not a bot."
                ),
            },
            {
                "role": "user",
                "content": f"News: {title}\nSummary: {summary}\nURL: {url}",
            },
        ]
        return await self._chat(messages, max_tokens=300)

    async def generate_newsletter_blurb(self, title: str, summary: str) -> str:
        """Short newsletter-style blurb for a single news item."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You write for a weekly AI newsletter. "
                    "Write a snappy 1–2 sentence blurb for a news item. "
                    "Start with an active verb. Keep it crisp and interesting."
                ),
            },
            {
                "role": "user",
                "content": f"{title}: {summary}",
            },
        ]
        return await self._chat(messages, max_tokens=100)

    async def score_impact(self, title: str, summary: str) -> int:
        """
        Score how impactful/important a piece of AI news is, 1–10.
        Returns integer.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI news editor. Rate the significance of this AI news "
                    "on a scale from 1 (trivial) to 10 (major breakthrough or industry shift). "
                    "Reply with a single integer only."
                ),
            },
            {
                "role": "user",
                "content": f"Title: {title}\nSummary: {summary}",
            },
        ]
        result = await self._chat(messages, max_tokens=5)
        try:
            return max(1, min(10, int(result.strip())))
        except ValueError:
            return 5

    async def are_duplicates(self, title_a: str, title_b: str) -> bool:
        """
        Lightweight semantic duplicate check for two titles.
        Returns True if they cover the same story.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You determine if two news headlines cover the same story. "
                    'Answer only "yes" or "no".'
                ),
            },
            {
                "role": "user",
                "content": f'Headline A: "{title_a}"\nHeadline B: "{title_b}"',
            },
        ]
        result = await self._chat(messages, max_tokens=5)
        return result.lower().startswith("yes")


groq_service = GroqService()
