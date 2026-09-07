from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Technicals:
    rsi: float
    ema_fast: float
    ema_slow: float
    macd: float
    macd_signal: float
    atr: float
    trend: str
    structure: str
    score: int


def _rsi(close: pd.Series, period: int = 14) -> float:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return float(val) if pd.notna(val) else 50.0


def _atr(df: pd.DataFrame, period: int = 14) -> float:
    high, low, close = df["High"], df["Low"], df["Close"]
    prev = close.shift(1)
    tr = pd.concat([(high - low), (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    val = tr.rolling(period).mean().iloc[-1]
    return float(val) if pd.notna(val) else float((high - low).iloc[-1])


def analyze(bars: pd.DataFrame) -> Technicals:
    if bars is None or bars.empty or len(bars) < 30:
        return Technicals(50, 0, 0, 0, 0, 0, "unknown", "insufficient data", 0)

    close = bars["Close"].astype(float)
    ema_fast = float(close.ewm(span=9, adjust=False).mean().iloc[-1])
    ema_slow = float(close.ewm(span=21, adjust=False).mean().iloc[-1])
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_v = float(macd.iloc[-1])
    sig_v = float(signal.iloc[-1])
    rsi = _rsi(close)
    atr = _atr(bars)

    trend = "bullish" if ema_fast > ema_slow else "bearish"
    if rsi >= 70:
        structure = "overbought"
    elif rsi <= 30:
        structure = "oversold"
    elif abs(ema_fast - ema_slow) / max(ema_slow, 1) < 0.0004:
        structure = "compressed"
    else:
        structure = "trending"

    score = 0
    score += 25 if ema_fast > ema_slow else -25
    score += 20 if macd_v > sig_v else -20
    if rsi > 55:
        score += 15
    elif rsi < 45:
        score -= 15
    if structure == "overbought":
        score -= 10
    if structure == "oversold":
        score += 10
    score = int(max(-100, min(100, score)))
    return Technicals(rsi, ema_fast, ema_slow, macd_v, sig_v, atr, trend, structure, score)
