from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    newsapi_key: str
    allowed_user_ids: frozenset[int]
    alert_interval_sec: int
    alert_min_score: int


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env")
    raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
    ids: set[int] = set()
    if raw_ids:
        for part in raw_ids.split(","):
            part = part.strip()
            if part:
                ids.add(int(part))
    return Settings(
        telegram_token=token,
        newsapi_key=os.getenv("NEWSAPI_KEY", "").strip(),
        allowed_user_ids=frozenset(ids),
        alert_interval_sec=int(os.getenv("ALERT_INTERVAL_SEC", "180")),
        alert_min_score=int(os.getenv("ALERT_MIN_SCORE", "68")),
    )
