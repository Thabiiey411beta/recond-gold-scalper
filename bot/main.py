from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.config import load_settings
from bot.engine import render_macro, render_news, render_scan, run_scan

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("recond")

SETTINGS = load_settings()
_cache_scan = None


def _allowed(update: Update) -> bool:
    if not SETTINGS.allowed_user_ids:
        return True
    uid = update.effective_user.id if update.effective_user else 0
    return uid in SETTINGS.allowed_user_ids


async def _deny(update: Update) -> None:
    if update.message:
        await update.message.reply_text("Access locked. Add your Telegram user id to ALLOWED_USER_IDS.")


def get_scan(force: bool = False):
    global _cache_scan
    if force or _cache_scan is None:
        _cache_scan = run_scan(SETTINGS.newsapi_key)
    return _cache_scan


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    await update.message.reply_text(
        "Recond Gold Scalper is live.\n"
        "I fuse XAU technicals, USD/yields, news sentiment, and political/macro risk.\n\n"
        "/scan full multi-factor read\n"
        "/signal bias + SL/TP\n"
        "/price gold and DXY\n"
        "/news headlines\n"
        "/macro calendar / geo risk\n"
        "/sentiment headline score\n\n"
        "Not financial advice. Scalping gold without a spread filter is how accounts die."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_start(update, context)


async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    await update.message.reply_text("Scanning gold tape...")
    try:
        scan = get_scan(force=True)
        await update.message.reply_text(render_scan(scan), parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        log.exception("scan failed")
        await update.message.reply_text(f"Scan failed: {exc}")


async def cmd_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    try:
        scan = get_scan(force=True)
        s = scan.signal
        text = (
            f"*{s.bias}*  conf {s.confidence}%\n"
            f"{s.action}\n"
            f"Entry `{s.entry:.2f}` SL `{s.sl:.2f}`\n"
            f"TP1 `{s.tp1:.2f}` TP2 `{s.tp2:.2f}`"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        await update.message.reply_text(f"Signal failed: {exc}")


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    scan = get_scan(force=True)
    p = scan.price
    dxy = f"{p.dxy:.2f} ({p.dxy_chg_pct:+.2f}%)" if p.dxy and p.dxy_chg_pct is not None else "n/a"
    yld = f"{p.us10y:.3f}" if p.us10y else "n/a"
    slv = f"{p.silver:.2f}" if p.silver else "n/a"
    await update.message.reply_text(
        f"Gold `{p.gold:.2f}` ({p.gold_chg_pct:+.2f}%)\nDXY {dxy}\nUS10Y {yld}\nSilver {slv}",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    scan = get_scan(force=True)
    await update.message.reply_text(render_news(scan), parse_mode=ParseMode.MARKDOWN)


async def cmd_macro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    scan = get_scan(force=True)
    await update.message.reply_text(render_macro(scan), parse_mode=ParseMode.MARKDOWN)


async def cmd_sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _allowed(update):
        return await _deny(update)
    scan = get_scan(force=True)
    s = scan.sentiment
    extra = ""
    if s.bull_hits:
        extra += "\nBull tags: " + ", ".join(s.bull_hits)
    if s.bear_hits:
        extra += "\nBear tags: " + ", ".join(s.bear_hits)
    await update.message.reply_text(f"{s.label}\nScore `{s.score}`{extra}", parse_mode=ParseMode.MARKDOWN)


def build_app() -> Application:
    app = Application.builder().token(SETTINGS.telegram_token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("signal", cmd_signal))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("macro", cmd_macro))
    app.add_handler(CommandHandler("sentiment", cmd_sentiment))
    return app


def main() -> None:
    log.info("Starting Recond Gold Scalper")
    build_app().run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
