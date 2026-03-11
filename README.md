# ETF / Spot Ratio Dashboard

Calculates live conversion ratios between ETFs and their underlying spot prices:

| ETF   | Underlying | Asset    |
|-------|-----------|----------|
| GLD   | XAUUSD    | Gold     |
| SLV   | XAGUSD    | Silver   |
| IBIT  | BTCUSD    | Bitcoin  |
| ETHA  | ETHUSD    | Ethereum |

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How it works

- Pulls hourly data via yfinance
- Gold/Silver spot proxied by front-month futures (GC=F, SI=F) since yfinance doesn't have direct XAUUSD/XAGUSD
- Only uses timestamps where **both** the ETF and underlying have trades (inner join), so the ratio is computed on overlapping market hours only
- Includes a two-way converter: enter a spot price to get the ETF equivalent, or vice versa
