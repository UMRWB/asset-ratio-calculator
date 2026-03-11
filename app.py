import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import time

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ETF / Spot Ratio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}
.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* Header */
.header-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.header-sub {
    text-align: center;
    color: #8892a4;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

/* Metric cards */
.ratio-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.ratio-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.card-label {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.card-ratio {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.3rem;
}
.card-prices {
    font-size: 0.78rem;
    color: #6b7280;
    line-height: 1.5;
}

/* Color accents per pair */
.accent-gold { color: #fbbf24; border-color: rgba(251,191,36,0.3); }
.accent-silver { color: #94a3b8; border-color: rgba(148,163,184,0.3); }
.accent-btc { color: #f97316; border-color: rgba(249,115,22,0.3); }
.accent-eth { color: #818cf8; border-color: rgba(129,140,248,0.3); }

/* Converter section */
.converter-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
}
.section-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 1rem;
}

/* Tabs */
div[data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
button[data-baseweb="tab"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    font-weight: 500 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(99,102,241,0.2) !important;
    color: #a5b4fc !important;
    border-color: rgba(99,102,241,0.4) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ─── Pair Definitions ──────────────────────────────────────────────────────────
PAIRS = {
    "GLD / XAUUSD": {
        "etf": "GLD",
        "spot": "GC=F",
        "spot_label": "XAUUSD",
        "accent": "gold",
        "color": "#fbbf24",
        "description": "Gold ETF vs Gold Spot",
    },
    "SLV / XAGUSD": {
        "etf": "SLV",
        "spot": "SI=F",
        "spot_label": "XAGUSD",
        "accent": "silver",
        "color": "#94a3b8",
        "description": "Silver ETF vs Silver Spot",
    },
    "IBIT / BTCUSD": {
        "etf": "IBIT",
        "spot": "BTC-USD",
        "spot_label": "BTCUSD",
        "accent": "btc",
        "color": "#f97316",
        "description": "Bitcoin ETF vs Bitcoin Spot",
    },
    "ETHA / ETHUSD": {
        "etf": "ETHA",
        "spot": "ETH-USD",
        "spot_label": "ETHUSD",
        "accent": "eth",
        "color": "#818cf8",
        "description": "Ethereum ETF vs Ethereum Spot",
    },
}


# ─── Data Fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_pair_data(etf_ticker, spot_ticker, days=30):
    """Fetch hourly data for an ETF and its underlying, aligned to overlapping hours."""
    end = datetime.now(pytz.timezone("US/Eastern"))
    start = end - timedelta(days=days)

    #etf_df = yf.download(etf_ticker, start=start, end=end, interval="1m", progress=False, auto_adjust=True)
    #spot_df = yf.download(spot_ticker, start=start, end=end, interval="1m", progress=False, auto_adjust=True)

    etf = yf.Ticker(etf_ticker)
    time.sleep(1)
    spot = yf.Ticker(spot_ticker)
    time.sleep(1)
    etf_df = etf.history(start=start, end=end, interval="5m")
    spot_df = spot.history(start=start, end=end, interval="5m")
    

    st.write(etf_df)
    st.write(spot_df)

    if etf_df.empty or spot_df.empty:
        return pd.DataFrame()

    # Flatten multi-index columns if present
    if isinstance(etf_df.columns, pd.MultiIndex):
        etf_df.columns = etf_df.columns.get_level_values(0)
    if isinstance(spot_df.columns, pd.MultiIndex):
        spot_df.columns = spot_df.columns.get_level_values(0)

    etf_close = etf_df[["Close"]].rename(columns={"Close": "ETF_Close"})
    spot_close = spot_df[["Close"]].rename(columns={"Close": "Spot_Close"})

    # Both indexes to UTC-naive for merge
    if etf_close.index.tz is not None:
        etf_close.index = etf_close.index.tz_convert("UTC").tz_localize(None)
    if spot_close.index.tz is not None:
        spot_close.index = spot_close.index.tz_convert("UTC").tz_localize(None)

    # Inner join: only keep timestamps where BOTH instruments have data
    merged = etf_close.join(spot_close, how="inner").dropna()

    st.write(merged)

    if merged.empty:
        return pd.DataFrame()
    
    merged["Ratio"] = merged["ETF_Close"] / merged["Spot_Close"]
    return merged


@st.cache_data(ttl=300, show_spinner=False)
def get_latest_prices(etf_ticker, spot_ticker):
    """Get the most recent closing prices for both instruments."""
    etf = yf.Ticker(etf_ticker)
    time.sleep(1)
    spot = yf.Ticker(spot_ticker)
    time.sleep(1)
    etf_hist = etf.history(period="5d", interval="5m")
    spot_hist = spot.history(period="5d", interval="5m")

    if isinstance(etf_hist.columns, pd.MultiIndex):
        etf_hist.columns = etf_hist.columns.get_level_values(0)
    if isinstance(spot_hist.columns, pd.MultiIndex):
        spot_hist.columns = spot_hist.columns.get_level_values(0)

    etf_price = float(etf_hist["Close"].dropna().iloc[-1]) if not etf_hist.empty else None
    spot_price = float(spot_hist["Close"].dropna().iloc[-1]) if not spot_hist.empty else None
    return etf_price, spot_price


# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="header-title">ETF / Spot Ratio Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Live conversion ratios between ETFs and their underlying spot prices. Only overlapping market hours are used.</div>', unsafe_allow_html=True)

# ─── Load Data ─────────────────────────────────────────────────────────────────
with st.spinner("Fetching market data..."):
    all_data = {}
    latest = {}
    for name, cfg in PAIRS.items():
        all_data[name] = fetch_pair_data(cfg["etf"], cfg["spot"])
        latest[name] = get_latest_prices(cfg["etf"], cfg["spot"])

# ─── Ratio Cards ───────────────────────────────────────────────────────────────
cols = st.columns(4, gap="medium")
for i, (name, cfg) in enumerate(PAIRS.items()):
    etf_price, spot_price = latest[name]
    df = all_data[name]
    current_ratio = etf_price / spot_price if (etf_price and spot_price) else None
    avg_ratio = float(df["Ratio"].mean()) if not df.empty else None

    with cols[i]:
        ratio_display = f"{current_ratio:.6f}" if current_ratio else "N/A"
        etf_display = f"${etf_price:,.2f}" if etf_price else "N/A"
        spot_display = f"${spot_price:,.2f}" if spot_price else "N/A"
        avg_display = f"Avg: {avg_ratio:.6f}" if avg_ratio else ""

        st.markdown(f"""
        <div class="ratio-card accent-{cfg['accent']}">
            <div class="card-label accent-{cfg['accent']}">{cfg['description']}</div>
            <div class="card-ratio">{ratio_display}</div>
            <div class="card-prices">
                {cfg['etf']}: {etf_display}<br>
                {cfg['spot_label']}: {spot_display}<br>
                <span style="color:#4b5563;">{avg_display}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Charts ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Ratio History (Hourly, Overlapping Hours Only)</div>', unsafe_allow_html=True)

period_options = {"7 Days": 7, "14 Days": 14, "30 Days": 30}
selected_period = st.radio("Lookback", list(period_options.keys()), horizontal=True, index=2, label_visibility="collapsed")
days = period_options[selected_period]

tab_names = list(PAIRS.keys())
tabs = st.tabs(tab_names)

for idx, (name, cfg) in enumerate(PAIRS.items()):
    with tabs[idx]:
        df = fetch_pair_data(cfg["etf"], cfg["spot"], days=days)
        if df.empty:
            st.warning(f"No overlapping data found for {name}.")
            continue

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.55, 0.45],
            subplot_titles=[f"{cfg['etf']} vs {cfg['spot_label']} Prices", "Conversion Ratio"]
        )

        # Price traces
        fig.add_trace(go.Scatter(
            x=df.index, y=df["ETF_Close"],
            name=cfg["etf"], line=dict(color=cfg["color"], width=2),
            hovertemplate="%{x}<br>" + cfg["etf"] + ": $%{y:.2f}<extra></extra>"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df["Spot_Close"],
            name=cfg["spot_label"], line=dict(color="#64748b", width=2),
            yaxis="y2",
            hovertemplate="%{x}<br>" + cfg["spot_label"] + ": $%{y:.2f}<extra></extra>"
        ), row=1, col=1)

        # Ratio trace
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Ratio"],
            name="Ratio", fill="tozeroy",
            line=dict(color=cfg["color"], width=2),
            # fillcolor=cfg["color"].replace(")", ",0.1)").replace("rgb", "rgba") if "rgb" in cfg["color"] else f"{cfg['color']}1a",
            hovertemplate="%{x}<br>Ratio: %{y:.6f}<extra></extra>"
        ), row=2, col=1)

        # Mean ratio line
        mean_ratio = df["Ratio"].mean()
        fig.add_hline(y=mean_ratio, line_dash="dash", line_color="#4b5563",
                      annotation_text=f"Mean: {mean_ratio:.6f}",
                      annotation_font_color="#6b7280", row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=550,
            margin=dict(l=60, r=20, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=11, color="#94a3b8")),
            font=dict(family="Inter", color="#94a3b8"),
            hovermode="x unified",
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)

        st.plotly_chart(fig, use_container_width=True)

        # Stats row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Ratio", f"{df['Ratio'].iloc[-1]:.6f}")
        c2.metric("Mean", f"{mean_ratio:.6f}")
        c3.metric("Min", f"{df['Ratio'].min():.6f}")
        c4.metric("Max", f"{df['Ratio'].max():.6f}")

# ─── Converter ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🔄 Price Converter</div>', unsafe_allow_html=True)
st.caption("Convert between ETF and spot prices using the current ratio.")

conv_col1, conv_col2 = st.columns(2, gap="large")

with conv_col1:
    st.markdown('<div class="converter-box">', unsafe_allow_html=True)
    st.markdown("**Spot → ETF**")
    pair_choice_1 = st.selectbox("Pair", list(PAIRS.keys()), key="conv1_pair", label_visibility="collapsed")
    cfg1 = PAIRS[pair_choice_1]
    etf_p1, spot_p1 = latest[pair_choice_1]
    ratio1 = etf_p1 / spot_p1 if (etf_p1 and spot_p1) else 0

    spot_input = st.number_input(
        f"Enter {cfg1['spot_label']} price",
        min_value=0.0,
        value=float(spot_p1) if spot_p1 else 0.0,
        format="%.4f",
        key="spot_input"
    )
    if ratio1:
        converted_etf = spot_input * ratio1
        st.success(f"**{cfg1['etf']} ≈ ${converted_etf:,.4f}**")
        st.caption(f"Using ratio: {ratio1:.6f}")
    st.markdown('</div>', unsafe_allow_html=True)

with conv_col2:
    st.markdown('<div class="converter-box">', unsafe_allow_html=True)
    st.markdown("**ETF → Spot**")
    pair_choice_2 = st.selectbox("Pair", list(PAIRS.keys()), key="conv2_pair", label_visibility="collapsed")
    cfg2 = PAIRS[pair_choice_2]
    etf_p2, spot_p2 = latest[pair_choice_2]
    ratio2 = etf_p2 / spot_p2 if (etf_p2 and spot_p2) else 0

    etf_input = st.number_input(
        f"Enter {cfg2['etf']} price",
        min_value=0.0,
        value=float(etf_p2) if etf_p2 else 0.0,
        format="%.4f",
        key="etf_input"
    )
    if ratio2:
        converted_spot = etf_input / ratio2
        st.success(f"**{cfg2['spot_label']} ≈ ${converted_spot:,.4f}**")
        st.caption(f"Using ratio: {ratio2:.6f}")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#4b5563; font-size:0.75rem; padding:1rem 0;">
    Data via Yahoo Finance. Ratios computed on overlapping market hours only.<br>
    Gold/Silver spot proxied by front-month futures (GC=F, SI=F). Crypto spot via BTC-USD, ETH-USD.<br>
    Prices refresh every 5 minutes. Not financial advice.
</div>
""", unsafe_allow_html=True)
