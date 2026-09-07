from __future__ import annotations

from dataclasses import dataclass

from bot.data.news import Headline

BULLISH = {
    "safe haven", "safe-haven", "rate cut", "dovish", "weak dollar", "weaker dollar",
    "geopolitical", "war", "escalat", "sanctions", "inflation surprise",
    "central bank buying", "gold rall", "record high", "flight to safety", "risk off", "risk-off",
}
BEARISH = {
    "hawkish", "rate hike", "strong dollar", "stronger dollar", "yields jump", "yields rise",
    "risk on", "risk-on", "profit taking", "gold slump", "gold fall", "gold drop",
    "peace talks", "ceasefire", "hot jobs", "hot cpi", "hot inflation",
}


@dataclass
class Sentiment:
    score: int
    label: str
    bull_hits: list[str]
    bear_hits: list[str]


def score_headlines(headlines: list[Headline]) -> Sentiment:
    text = " | ".join(h.title.lower() for h in headlines)
    bulls = [k for k in BULLISH if k in text]
    bears = [k for k in BEARISH if k in text]
    raw = 12 * len(bulls) - 12 * len(bears)
    if "gold" in text and not bulls and not bears:
        raw = 0
    score = int(max(-100, min(100, raw)))
    if score >= 25:
        label = "risk-on for gold (bullish flow)"
    elif score <= -25:
        label = "risk-off for gold (bearish flow)"
    else:
        label = "mixed / neutral"
    return Sentiment(score=score, label=label, bull_hits=bulls[:6], bear_hits=bears[:6])
