from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import feedparser
import httpx

GOLD_FEEDS = [
    "https://news.google.com/rss/search?q=gold+price+OR+XAUUSD+OR+XAU+USD+Fed+OR+geopolitics&hl=en-US&gl=US&ceid=US:en",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.kitco.com/rss/KitcoNews.xml",
]

KEYWORDS = (
    "gold", "xau", "xauusd", "fed", "fomc", "powell", "yield", "dollar", "dxy",
    "inflation", "cpi", "nfp", "treasury", "war", "sanctions", "tariff",
    "election", "geopolit", "israel", "ukraine", "china", "rate",
)


@dataclass
class Headline:
    title: str
    source: str
    link: str


def _from_rss(url: str, limit: int = 12) -> list[Headline]:
    parsed = feedparser.parse(url)
    out: list[Headline] = []
    for e in parsed.entries[:limit]:
        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        source = parsed.feed.get("title", url)
        if title:
            out.append(Headline(title=title, source=str(source), link=link))
    return out


def _from_newsapi(api_key: str) -> list[Headline]:
    if not api_key:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "gold OR XAUUSD OR FOMC OR geopolitics OR dollar OR inflation",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": api_key,
    }
    try:
        r = httpx.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    out = []
    for a in data.get("articles", []):
        title = (a.get("title") or "").strip()
        if title:
            out.append(Headline(title=title, source=(a.get("source") or {}).get("name") or "NewsAPI", link=a.get("url") or ""))
    return out


def _relevant(h: Headline) -> bool:
    t = h.title.lower()
    return any(k in t for k in KEYWORDS)


def fetch_headlines(newsapi_key: str = "") -> list[Headline]:
    items: list[Headline] = []
    items.extend(_from_newsapi(newsapi_key))
    for feed in GOLD_FEEDS:
        try:
            items.extend(_from_rss(feed))
        except Exception:
            continue
    seen: set[str] = set()
    unique: list[Headline] = []
    for h in items:
        key = h.title.lower()
        if key in seen:
            continue
        seen.add(key)
        if _relevant(h) or "gold" in key or "fed" in key:
            unique.append(h)
    return unique[:25]


def format_headlines(items: Iterable[Headline], n: int = 8) -> str:
    lines = [f"- {h.title}" for h in list(items)[:n]]
    return "\n".join(lines) if lines else "No fresh gold/USD headlines."
