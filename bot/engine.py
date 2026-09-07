from __future__ import annotations

from dataclasses import dataclass

from bot.data.macro import analyze_macro, fetch_calendar
from bot.data.news import Headline, fetch_headlines
from bot.data.price import PriceSnapshot, fetch_snapshot
from bot.data.sentiment import Sentiment, score_headlines
from bot.data.technicals import Technicals, analyze
from bot.strategy import Signal, fuse


@dataclass
class Scan:
    price: PriceSnapshot
    tech5: Technicals
    tech15: Technicals
    headlines: list[Headline]
    sentiment: Sentiment
    signal: Signal
    macro_label: str
    political: list[str]


def run_scan(newsapi_key: str = "") -> Scan:
    price = fetch_snapshot()
    tech5 = analyze(price.bars_5m)
    tech15 = analyze(price.bars_15m)
    headlines = fetch_headlines(newsapi_key)
    sentiment = score_headlines(headlines)
    events = fetch_calendar()
    macro = analyze_macro(events)
    signal = fuse(price, tech5, tech15, sentiment, macro)
    return Scan(price, tech5, tech15, headlines, sentiment, signal, macro.risk_label, macro.political_hits)


def render_scan(scan: Scan) -> str:
    p, s, t5 = scan.price, scan.signal, scan.tech5
    dxy = f"{p.dxy:.2f}" if p.dxy else "n/a"
    lines = [
        "*Recond Gold Scalper*",
        f"XAU `{p.gold:.2f}`  ({p.gold_chg_pct:+.2f}% d)",
        f"DXY `{dxy}`   ATR `{t5.atr:.2f}`",
        "",
        f"*Bias:* {s.bias}   *Conf:* {s.confidence}%",
        f"*Action:* {s.action}",
        f"Entry `{s.entry:.2f}`  SL `{s.sl:.2f}`",
        f"TP1 `{s.tp1:.2f}`  TP2 `{s.tp2:.2f}`",
        f"Fused score `{s.fused}`",
        "",
        "*Why*",
        *[f"- {r}" for r in s.reasons],
        "",
        f"*Sentiment:* {scan.sentiment.label}",
        f"*Macro:* {scan.macro_label}",
    ]
    if scan.political:
        lines.append("*Political / geo:*")
        lines.extend(f"- {x}" for x in scan.political[:4])
    lines += ["", "_Research only. Gold spreads + news spikes kill naive scalps. Demo first._"]
    return "\n".join(lines)


def render_news(scan: Scan) -> str:
    if not scan.headlines:
        return "No headlines pulled."
    lines = ["*Gold / USD tape*"]
    for h in scan.headlines[:10]:
        lines.append(f"- {h.title}")
    return "\n".join(lines)


def render_macro(scan: Scan) -> str:
    lines = ["*Macro / political risk*", scan.macro_label]
    if scan.political:
        lines.append("")
        lines.extend(f"- {x}" for x in scan.political[:8])
    else:
        lines.append("No explicit political calendar tags in this week's feed.")
    return "\n".join(lines)
