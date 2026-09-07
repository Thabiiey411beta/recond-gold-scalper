from __future__ import annotations

from dataclasses import dataclass

from bot.data.macro import MacroBook
from bot.data.price import PriceSnapshot
from bot.data.sentiment import Sentiment
from bot.data.technicals import Technicals


@dataclass
class Signal:
    bias: str
    action: str
    confidence: int
    entry: float
    sl: float
    tp1: float
    tp2: float
    reasons: list[str]
    fused: int


def fuse(price: PriceSnapshot, tech5: Technicals, tech15: Technicals, sentiment: Sentiment, macro: MacroBook) -> Signal:
    tech = int(0.6 * tech5.score + 0.4 * tech15.score)
    fused = int(0.55 * tech + 0.25 * sentiment.score + 0.20 * macro.score)
    fused = max(-100, min(100, fused))
    reasons = [
        f"M5 {tech5.trend}/{tech5.structure} RSI {tech5.rsi:.1f}",
        f"M15 {tech15.trend} MACD {tech15.macd:.2f}",
        f"News {sentiment.label} ({sentiment.score})",
        f"Macro {macro.risk_label}",
    ]
    if price.dxy is not None and price.dxy_chg_pct is not None:
        reasons.append(f"DXY {price.dxy:.2f} ({price.dxy_chg_pct:+.2f}%)")
    if price.us10y is not None:
        reasons.append(f"US10Y {price.us10y:.3f}")
    atr = tech5.atr or max(price.gold * 0.0008, 1.2)
    entry = price.gold
    if price.dxy_chg_pct is not None:
        if price.dxy_chg_pct > 0.25:
            fused -= 8
            reasons.append("USD bid - gold headwind")
        elif price.dxy_chg_pct < -0.25:
            fused += 8
            reasons.append("USD offer - gold tailwind")
    if macro.high_impact_usd >= 2 or "HIGH" in macro.risk_label:
        return Signal("FLAT", "NO TRADE - event / political risk", abs(fused), entry, entry, entry, entry, reasons, fused)
    if fused >= 28:
        return Signal("LONG", "Scalp BUY pullback / break", min(95, 40 + abs(fused) // 2), entry, entry - 1.2 * atr, entry + 0.9 * atr, entry + 1.6 * atr, reasons, fused)
    if fused <= -28:
        return Signal("SHORT", "Scalp SELL rally / breakdown", min(95, 40 + abs(fused) // 2), entry, entry + 1.2 * atr, entry - 0.9 * atr, entry - 1.6 * atr, reasons, fused)
    return Signal("RANGE", "WAIT - mixed tape, no edge", min(95, 40 + abs(fused) // 2), entry, entry - atr, entry + 0.6 * atr, entry + atr, reasons, fused)
