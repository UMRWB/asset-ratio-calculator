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
.accent-gold2 { color: #d97706; border-color: rgba(217,119,6,0.3); }
.accent-silver { color: #94a3b8; border-color: rgba(148,163,184,0.3); }
.accent-silver2 { color: #64748b; border-color: rgba(100,116,139,0.3); }
.accent-btc { color: #f97316; border-color: rgba(249,115,22,0.3); }
.accent-btc2 { color: #ea580c; border-color: rgba(234,88,12,0.3); }
.accent-eth { color: #818cf8; border-color: rgba(129,140,248,0.3); }
.accent-eth2 { color: #6366f1; border-color: rgba(99,102,241,0.3); }

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
        "inverse": False,
    },
    "GLL / XAUUSD": {
        "etf": "GLL",
        "spot": "GC=F",
        "spot_label": "XAUUSD",
        "accent": "gold2",
        "color": "#d97706",
        "description": "UltraShort Gold vs Gold Spot",
        "inverse": True,
    },
    "SLV / XAGUSD": {
        "etf": "SLV",
        "spot": "SI=F",
        "spot_label": "XAGUSD",
        "accent": "silver",
        "color": "#94a3b8",
        "description": "Silver ETF vs Silver Spot",
        "inverse": False,
    },
    "AGQ / XAGUSD": {
        "etf": "AGQ",
        "spot": "SI=F",
        "spot_label": "XAGUSD",
        "accent": "silver2",
        "color": "#64748b",
        "description": "Ultra Silver vs Silver Spot",
        "inverse": True,
    },
    "IBIT / BTCUSD": {
        "etf": "IBIT",
        "spot": "BTC-USD",
        "spot_label": "BTCUSD",
        "accent": "btc",
        "color": "#f97316",
        "description": "Bitcoin ETF vs Bitcoin Spot",
        "inverse": False,
    },
    "SBIT / BTCUSD": {
        "etf": "SBIT",
        "spot": "BTC-USD",
        "spot_label": "BTCUSD",
        "accent": "btc2",
        "color": "#ea580c",
        "description": "Short Bitcoin vs Bitcoin Spot",
        "inverse": True,
    },
    "ETHA / ETHUSD": {
        "etf": "ETHA",
        "spot": "ETH-USD",
        "spot_label": "ETHUSD",
        "accent": "eth",
        "color": "#818cf8",
        "description": "Ethereum ETF vs Ethereum Spot",
        "inverse": False,
    },
    "ETHD / ETHUSD": {
        "etf": "ETHD",
        "spot": "ETH-USD",
        "spot_label": "ETHUSD",
        "accent": "eth2",
        "color": "#6366f1",
        "description": "Short Ether vs Ether Spot",
        "inverse": True,
    },
}


# ─── Single Data Fetch (minimise API calls) ───────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_pairs():
    """
    Fetch 30 days of 5m data for ALL pairs in a single cached call.
    Spot tickers shared across pairs (e.g. GC=F for GLD & GLL) are fetched
    only once and reused, saving API calls.
    After merging to overlapping timestamps, keeps only the last 100 rows.

    Total yfinance calls: 12 (8 unique ETFs + 4 unique spots), with 0.5s sleeps.
    """
    results = {}
    spot_cache = {}  # { ticker_str: DataFrame } — avoids re-fetching shared spots

    def fetch_ticker(ticker_str):
        """Fetch a single ticker's 30d/5m history."""
        t = yf.Ticker(ticker_str)
        time.sleep(0.5)
        df = t.history(period="30d", interval="5m")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if not df.empty and df.index.tz is not None:
            df.index = df.index.tz_convert("UTC").tz_localize(None)
        return df

    for name, cfg in PAIRS.items():
        try:
            # Fetch ETF (always unique per pair)
            etf_df = fetch_ticker(cfg["etf"])

            # Fetch spot — reuse if already downloaded
            spot_ticker = cfg["spot"]
            if spot_ticker not in spot_cache:
                spot_cache[spot_ticker] = fetch_ticker(spot_ticker)
            spot_df = spot_cache[spot_ticker]

            if etf_df.empty or spot_df.empty:
                results[name] = pd.DataFrame()
                continue

            etf_close = etf_df[["Close"]].rename(columns={"Close": "ETF_Close"})
            spot_close = spot_df[["Close"]].rename(columns={"Close": "Spot_Close"})

            # Inner join: only overlapping timestamps
            merged = etf_close.join(spot_close, how="inner").dropna()

            if merged.empty:
                results[name] = pd.DataFrame()
                continue

            # Ratio: ETF/Spot for standard, ETF×Spot for inverse
            if cfg.get("inverse", False):
                merged["Ratio"] = merged["ETF_Close"] * merged["Spot_Close"]
            else:
                merged["Ratio"] = merged["ETF_Close"] / merged["Spot_Close"]
            # Keep only the last 100 overlapping data points
            merged = merged.tail(100)
            results[name] = merged

        except Exception as e:
            st.warning(f"Error fetching {name}: {e}")
            results[name] = pd.DataFrame()

    return results


# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="header-title">ETF / Spot Ratio Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Live conversion ratios between ETFs and their underlying spot prices · Last 100 overlapping data points · 5-min intervals</div>', unsafe_allow_html=True)

# ─── Load Data (single cached call) ───────────────────────────────────────────
with st.spinner("Fetching market data..."):
    all_data = fetch_all_pairs()

# ─── Ratio Cards ───────────────────────────────────────────────────────────────
pair_list = list(PAIRS.items())
for row_start in range(0, len(pair_list), 4):
    row_pairs = pair_list[row_start:row_start + 4]
    cols = st.columns(len(row_pairs), gap="medium")
    for i, (name, cfg) in enumerate(row_pairs):
        df = all_data[name]
        if not df.empty:
            latest_ratio = float(df["Ratio"].iloc[-1])
            etf_price = float(df["ETF_Close"].iloc[-1])
            spot_price = float(df["Spot_Close"].iloc[-1])
            avg_ratio = float(df["Ratio"].mean())
        else:
            latest_ratio = etf_price = spot_price = avg_ratio = None

        with cols[i]:
            is_inv = cfg.get("inverse", False)
            formula = f"{cfg['etf']}×{cfg['spot_label']}" if is_inv else f"{cfg['etf']}/{cfg['spot_label']}"
            # Smart formatting: large ratios (inverse) use fewer decimals
            if latest_ratio is not None:
                ratio_display = f"{latest_ratio:,.2f}" if latest_ratio > 10 else f"{latest_ratio:.6f}"
            else:
                ratio_display = "N/A"
            etf_display = f"${etf_price:,.2f}" if etf_price else "N/A"
            spot_display = f"${spot_price:,.2f}" if spot_price else "N/A"
            if avg_ratio is not None:
                avg_display = f"Avg: {avg_ratio:,.2f}" if avg_ratio > 10 else f"Avg: {avg_ratio:.6f}"
            else:
                avg_display = ""

            st.markdown(f"""
            <div class="ratio-card accent-{cfg['accent']}">
                <div class="card-label accent-{cfg['accent']}">{cfg['description']}</div>
                <div class="card-ratio">{ratio_display}</div>
                <div class="card-prices">
                    <span style="color:#4b5563; font-size:0.7rem;">{formula}</span><br>
                    {cfg['etf']}: {etf_display}<br>
                    {cfg['spot_label']}: {spot_display}<br>
                    <span style="color:#4b5563;">{avg_display}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    if row_start == 0:
        st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Charts ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Ratio History — Last 100 Data Points (Overlapping Hours Only)</div>', unsafe_allow_html=True)

tab_names = list(PAIRS.keys())
tabs = st.tabs(tab_names)

for idx, (name, cfg) in enumerate(PAIRS.items()):
    with tabs[idx]:
        df = all_data[name]
        if df.empty:
            st.warning(f"No overlapping data found for {name}.")
            continue

        # ── Normalize prices to % change from first data point ──
        df = df.copy()
        etf_base = df["ETF_Close"].iloc[0]
        spot_base = df["Spot_Close"].iloc[0]
        df["ETF_Pct"] = (df["ETF_Close"] / etf_base - 1) * 100
        df["Spot_Pct"] = (df["Spot_Close"] / spot_base - 1) * 100

        ratio_formula = f"{cfg['etf']} × {cfg['spot_label']}" if cfg.get("inverse") else f"{cfg['etf']} / {cfg['spot_label']}"
        is_inverse = cfg.get("inverse", False)

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.10,
            row_heights=[0.50, 0.50],
            subplot_titles=[
                f"{cfg['etf']} vs {cfg['spot_label']} — Normalized % Change",
                f"Conversion Ratio: {ratio_formula} (Zoomed)"
            ]
        )

        # ── Price chart: plot % change, show original $ on hover ──
        fig.add_trace(go.Scatter(
            x=df.index, y=df["ETF_Pct"],
            name=cfg["etf"],
            line=dict(color=cfg["color"], width=2),
            customdata=df["ETF_Close"],
            hovertemplate=(
                "%{x}<br>"
                + cfg["etf"] + ": <b>$%{customdata:.2f}</b> (%{y:+.2f}%)"
                + "<extra></extra>"
            )
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df["Spot_Pct"],
            name=cfg["spot_label"],
            line=dict(color="#64748b", width=2),
            customdata=df["Spot_Close"],
            hovertemplate=(
                "%{x}<br>"
                + cfg["spot_label"] + ": <b>$%{customdata:.2f}</b> (%{y:+.2f}%)"
                + "<extra></extra>"
            )
        ), row=1, col=1)

        # Zero reference line for % chart
        fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.15)", row=1, col=1)

        # ── Ratio chart: zoomed in, no fill-to-zero ──
        ratio_hover_fmt = "%{x}<br>Ratio: %{y:,.2f}<extra></extra>" if is_inverse else "%{x}<br>Ratio: %{y:.6f}<extra></extra>"
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Ratio"],
            name="Ratio",
            line=dict(color=cfg["color"], width=2),
            hovertemplate=ratio_hover_fmt
        ), row=2, col=1)

        # Stats from the 5-day dataset
        mean_ratio = df["Ratio"].mean()
        ratio_min = df["Ratio"].min()
        ratio_max = df["Ratio"].max()

        # Mean line on ratio chart
        mean_label = f"Mean: {mean_ratio:,.2f}" if mean_ratio > 10 else f"Mean: {mean_ratio:.6f}"
        fig.add_hline(y=mean_ratio, line_dash="dash", line_color="#4b5563",
                      annotation_text=mean_label,
                      annotation_font_color="#6b7280",
                      annotation_font_size=10, row=2, col=1)

        # Zoom the ratio y-axis: pad 20% above and below the data range
        ratio_range_span = ratio_max - ratio_min
        ratio_pad = max(ratio_range_span * 0.20, 1e-7)
        fig.update_yaxes(
            range=[ratio_min - ratio_pad, ratio_max + ratio_pad],
            row=2, col=1
        )

        # Subtle shaded band between min and max on ratio chart
        fig.add_trace(go.Scatter(
            x=df.index, y=[ratio_max] * len(df),
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip"
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=[ratio_min] * len(df),
            mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(255,255,255,0.03)",
            showlegend=False, hoverinfo="skip"
        ), row=2, col=1)

        # Y-axis labels
        fig.update_yaxes(title_text="% Change", row=1, col=1)
        fig.update_yaxes(title_text="Ratio", row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=650,
            margin=dict(l=70, r=20, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=11, color="#94a3b8")),
            font=dict(family="Inter", color="#94a3b8"),
            hovermode="x unified",
        )
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)", zeroline=False)

        st.plotly_chart(fig, use_container_width=True)

        # Stats row
        def fmt_ratio(v):
            return f"{v:,.2f}" if v > 10 else f"{v:.6f}"
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Ratio", fmt_ratio(df['Ratio'].iloc[-1]))
        c2.metric("Mean", fmt_ratio(mean_ratio))
        c3.metric("Min", fmt_ratio(ratio_min))
        c4.metric("Max", fmt_ratio(ratio_max))

# ─── Converter ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">🔄 Price Converter</div>', unsafe_allow_html=True)
st.caption("Convert between ETF and spot prices using your chosen ratio method.")

# ── Ratio method selector (shared across both converters) ──
RATIO_METHODS = {
    "Latest (overlapping)": "latest",
    "Mean": "mean",
    "Min": "min",
    "Max": "max",
}

ratio_method_label = st.radio(
    "Ratio method",
    list(RATIO_METHODS.keys()),
    horizontal=True,
    index=0,
    help="**Latest (overlapping)**: last ratio when both ETF & spot were open simultaneously. "
         "**Mean/Min/Max**: statistics over the last 100 overlapping data points. "
         "Standard pairs use ETF/Spot; inverse pairs (GLL, AGQ, SBIT, ETHD) use ETF×Spot."
)
ratio_method = RATIO_METHODS[ratio_method_label]


def get_ratio_for_pair(pair_name, method):
    """Return the ratio for a pair based on the chosen method."""
    df = all_data[pair_name]
    if df.empty:
        return None
    if method == "latest":
        return float(df["Ratio"].iloc[-1])
    elif method == "mean":
        return float(df["Ratio"].mean())
    elif method == "min":
        return float(df["Ratio"].min())
    elif method == "max":
        return float(df["Ratio"].max())
    return None


conv_col1, conv_col2 = st.columns(2, gap="large")

with conv_col1:
    st.markdown('<div class="converter-box">', unsafe_allow_html=True)
    st.markdown("**Spot → ETF**")
    pair_choice_1 = st.selectbox("Pair", list(PAIRS.keys()), key="conv1_pair", label_visibility="collapsed")
    cfg1 = PAIRS[pair_choice_1]
    ratio1 = get_ratio_for_pair(pair_choice_1, ratio_method)

    # Pre-fill with latest spot price from overlapping dataset
    df1 = all_data[pair_choice_1]
    default_spot = float(df1["Spot_Close"].iloc[-1]) if not df1.empty else 0.0

    spot_input = st.number_input(
        f"Enter {cfg1['spot_label']} price",
        min_value=0.0,
        value=default_spot,
        format="%.4f",
        key="spot_input"
    )
    if ratio1:
        is_inv_1 = cfg1.get("inverse", False)
        if is_inv_1:
            # Inverse: ratio = ETF × Spot → ETF = ratio / Spot
            converted_etf = ratio1 / spot_input if spot_input > 0 else 0
            formula_label = f"{cfg1['etf']} × {cfg1['spot_label']}"
        else:
            # Standard: ratio = ETF / Spot → ETF = ratio × Spot
            converted_etf = spot_input * ratio1
            formula_label = f"{cfg1['etf']} / {cfg1['spot_label']}"
        st.success(f"**{cfg1['etf']} ≈ ${converted_etf:,.4f}**")
        ratio_fmt = f"{ratio1:,.2f}" if ratio1 > 10 else f"{ratio1:.6f}"
        st.caption(f"Using {ratio_method_label.lower()} ratio ({formula_label}): {ratio_fmt}")
    else:
        st.warning("No overlapping data available to compute ratio.")
    st.markdown('</div>', unsafe_allow_html=True)

with conv_col2:
    st.markdown('<div class="converter-box">', unsafe_allow_html=True)
    st.markdown("**ETF → Spot**")
    pair_choice_2 = st.selectbox("Pair", list(PAIRS.keys()), key="conv2_pair", label_visibility="collapsed")
    cfg2 = PAIRS[pair_choice_2]
    ratio2 = get_ratio_for_pair(pair_choice_2, ratio_method)

    # Pre-fill with latest ETF price from overlapping dataset
    df2 = all_data[pair_choice_2]
    default_etf = float(df2["ETF_Close"].iloc[-1]) if not df2.empty else 0.0

    etf_input = st.number_input(
        f"Enter {cfg2['etf']} price",
        min_value=0.0,
        value=default_etf,
        format="%.4f",
        key="etf_input"
    )
    if ratio2:
        is_inv_2 = cfg2.get("inverse", False)
        if is_inv_2:
            # Inverse: ratio = ETF × Spot → Spot = ratio / ETF
            converted_spot = ratio2 / etf_input if etf_input > 0 else 0
            formula_label = f"{cfg2['etf']} × {cfg2['spot_label']}"
        else:
            # Standard: ratio = ETF / Spot → Spot = ETF / ratio
            converted_spot = etf_input / ratio2
            formula_label = f"{cfg2['etf']} / {cfg2['spot_label']}"
        st.success(f"**{cfg2['spot_label']} ≈ ${converted_spot:,.4f}**")
        ratio_fmt = f"{ratio2:,.2f}" if ratio2 > 10 else f"{ratio2:.6f}"
        st.caption(f"Using {ratio_method_label.lower()} ratio ({formula_label}): {ratio_fmt}")
    else:
        st.warning("No overlapping data available to compute ratio.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#4b5563; font-size:0.75rem; padding:1rem 0;">
    Data via Yahoo Finance · Last 100 overlapping data points from 30-day window · 5-min intervals<br>
    Gold/Silver spot proxied by front-month futures (GC=F, SI=F) · Crypto spot via BTC-USD, ETH-USD<br>
    Inverse ETFs (GLL, AGQ, SBIT, ETHD) use ETF×Spot ratio · Standard ETFs use ETF/Spot ratio<br>
    Cached for 5 minutes · Not financial advice
</div>
""", unsafe_allow_html=True)
