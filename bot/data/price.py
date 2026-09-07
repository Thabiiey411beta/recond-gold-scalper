from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import yfinance as yf


@dataclass
class PriceSnapshot:
    gold: float
    gold_chg_pct: float
    dxy: Optional[float]
    dxy_chg_pct: Optional[float]
    us10y: Optional[float]
    silver: Optional[float]
    bars_5m: pd.DataFrame
    bars_15m: pd.DataFrame


def _last_close_chg(ticker: str, period: str = "5d") -> tuple[Optional[float], Optional[float]]:
    hist = yf.Ticker(ticker).history(period=period, interval="1d")
    if hist is None or hist.empty:
        return None, None
    close = float(hist["Close"].iloc[-1])
    if len(hist) < 2:
        return close, None
    prev = float(hist["Close"].iloc[-2])
    chg = (close - prev) / prev * 100 if prev else None
    return close, chg


def fetch_snapshot() -> PriceSnapshot:
    gold, gold_chg = _last_close_chg("GC=F")
    if gold is None:
        gold, gold_chg = _last_close_chg("XAUUSD=X")
    dxy, dxy_chg = _last_close_chg("DX-Y.NYB")
    us10y, _ = _last_close_chg("^TNX")
    silver, _ = _last_close_chg("SI=F")

    bars_5m = yf.download("GC=F", period="5d", interval="5m", progress=False, auto_adjust=True)
    bars_15m = yf.download("GC=F", period="10d", interval="15m", progress=False, auto_adjust=True)
    if bars_5m is None or bars_5m.empty:
        bars_5m = yf.download("XAUUSD=X", period="5d", interval="5m", progress=False, auto_adjust=True)
    if bars_15m is None or bars_15m.empty:
        bars_15m = yf.download("XAUUSD=X", period="10d", interval="15m", progress=False, auto_adjust=True)

    if isinstance(bars_5m.columns, pd.MultiIndex):
        bars_5m.columns = [c[0] for c in bars_5m.columns]
    if isinstance(bars_15m.columns, pd.MultiIndex):
        bars_15m.columns = [c[0] for c in bars_15m.columns]

    live = gold
    if bars_5m is not None and not bars_5m.empty:
        live = float(bars_5m["Close"].iloc[-1])
        if gold is not None and gold_chg is None:
            gold_chg = 0.0

    return PriceSnapshot(
        gold=float(live or 0.0),
        gold_chg_pct=float(gold_chg or 0.0),
        dxy=dxy,
        dxy_chg_pct=dxy_chg,
        us10y=us10y,
        silver=silver,
        bars_5m=bars_5m if bars_5m is not None else pd.DataFrame(),
        bars_15m=bars_15m if bars_15m is not None else pd.DataFrame(),
    )
