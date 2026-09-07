from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

POLITICAL = (
    "election", "war", "sanction", "tariff", "geopolit", "military", "opec",
    "white house", "congress", "impeach", "ceasefire", "nato", "china",
    "taiwan", "iran", "russia", "ukraine", "israel",
)


@dataclass
class MacroEvent:
    title: str
    country: str
    impact: str
    when: str
    forecast: str
    previous: str


@dataclass
class MacroBook:
    events: list[MacroEvent]
    high_impact_usd: int
    political_hits: list[str]
    risk_label: str
    score: int


def _parse_when(raw: Any) -> str:
    if not raw:
        return "?"
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).strftime("%a %H:%M UTC")
    except Exception:
        return str(raw)[:16]


def fetch_calendar() -> list[MacroEvent]:
    try:
        r = httpx.get(FF_URL, timeout=20, headers={"User-Agent": "RecondGoldScalper/1.0"})
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    out: list[MacroEvent] = []
    if not isinstance(data, list):
        return out
    for row in data:
        country = str(row.get("country") or row.get("countryCode") or "")
        title = str(row.get("title") or row.get("event") or "")
        impact = str(row.get("impact") or row.get("volatility") or "").lower()
        out.append(MacroEvent(title=title, country=country, impact=impact, when=_parse_when(row.get("date") or row.get("datetime")), forecast=str(row.get("forecast") or ""), previous=str(row.get("previous") or "")))
    return out


def analyze_macro(events: list[MacroEvent]) -> MacroBook:
    usd_high = [e for e in events if e.country.upper() in {"USD", "US", "USA"} and ("high" in e.impact or e.impact == "red")]
    political: list[str] = []
    for e in events:
        blob = f"{e.title} {e.country}".lower()
        if any(k in blob for k in POLITICAL):
            political.append(f"{e.when} {e.country} {e.title}")
    caution = 18 * min(len(usd_high), 4) + 10 * min(len(political), 4)
    score = -int(min(100, caution))
    if caution >= 40:
        risk = "HIGH - prefer flat into event risk"
    elif caution >= 18:
        risk = "ELEVATED - reduce size / skip weak setups"
    else:
        risk = "NORMAL session risk"
    return MacroBook(events=events, high_impact_usd=len(usd_high), political_hits=political[:8], risk_label=risk, score=score)
