# Recond Gold Scalper

Telegram intelligence bot for **XAUUSD** attached to [@RecondTrade_Bot](https://t.me/RecondTrade_Bot).

It does **not** place broker orders. It fuses four live inputs into a scalp bias:

1. **Technicals** — M5/M15 EMA 9/21, RSI, MACD, ATR from Yahoo gold futures
2. **USD fundamentals** — DXY and US 10Y yield tilt
3. **News sentiment** — Google News / Reuters / Kitco RSS (+ optional NewsAPI)
4. **Political + macro risk** — this-week economic calendar; high-impact USD and geo tags can force **FLAT**

## Commands

| Command | What it does |
|---|---|
| `/scan` | Full multi-factor read + SL/TP |
| `/signal` | Bias only |
| `/price` | Gold, DXY, 10Y, silver |
| `/news` | Filtered tape |
| `/macro` | Calendar / political risk |
| `/sentiment` | Headline score |

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# put TELEGRAM_BOT_TOKEN in .env  — never commit it
python -m bot.main
```

Optional:

- `NEWSAPI_KEY` — richer headline coverage
- `ALLOWED_USER_IDS` — lock the bot to your Telegram id (`@userinfobot`)
- `ALERT_MIN_SCORE` — reserved for a later alert loop

## Honest limits

- Yahoo gold futures (`GC=F`) is a proxy for spot XAUUSD. Broker quotes differ.
- RSS sentiment is keyword-based, not an LLM.
- The Forex Factory JSON feed is unofficial and can break.
- Gold M1/M5 scalps die on spread, slippage, and red-folder prints. Demo first.
- This is research software, not financial advice.

## Security

BotFather tokens control the bot. Keep `.env` private. If a token was pasted in chat, rotate it at [@BotFather](https://t.me/BotFather) with `/revoke`.
