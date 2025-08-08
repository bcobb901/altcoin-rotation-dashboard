
import streamlit as st
import pandas as pd
import requests
from typing import Optional

st.set_page_config(page_title="Altcoin Season Rotation Dashboard", layout="wide")
st.title("🚀 Altcoin Season Rotation Dashboard (Public-Data Edition)")

# ------------------------------
# Sidebar controls
# ------------------------------
st.sidebar.header("⚙️ Controls")
st.sidebar.caption("Tune thresholds; add API keys later.")
btc_dom_threshold = st.sidebar.slider("BTC Dominance ↓ (rotate below %)", 35.0, 70.0, 50.0, 0.5)
ethbtc_bull_threshold = st.sidebar.slider("ETH/BTC ↑ (rotate when above)", 0.055, 0.12, 0.065, 0.001)
alt_season_index_key = st.sidebar.text_input("CoinGlass API Key (optional, for Altcoin Season Index)", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Notes")
st.sidebar.info(
    "This version uses ONLY public sources so it works out-of-the-box. "
    "Add your CoinGlass API key later to unlock the Altcoin Season Index panel."
)

# ------------------------------
# Helpers
# ------------------------------
@st.cache_data(ttl=300)
def get_fng() -> Optional[dict]:
    try:
        resp = requests.get("https://api.alternative.me/fng/?limit=1&format=json", timeout=20)
        resp.raise_for_status()
        data = resp.json()["data"][0]
        return {"value": int(data["value"]), "classification": data["value_classification"]}
    except Exception as e:
        st.warning(f"Fear & Greed fetch failed: {e}")
        return None

@st.cache_data(ttl=300)
def get_coingecko_global() -> Optional[dict]:
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/global", timeout=20, headers={"accept":"application/json"})
        resp.raise_for_status()
        return resp.json()["data"]
    except Exception as e:
        st.warning(f"CoinGecko global fetch failed: {e}")
        return None

@st.cache_data(ttl=300)
def get_eth_btc_ratio() -> Optional[float]:
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=btc", timeout=20)
        resp.raise_for_status()
        return float(resp.json()["ethereum"]["btc"])
    except Exception as e:
        st.warning(f"ETH/BTC fetch failed: {e}")
        return None

@st.cache_data(ttl=600)
def get_coingecko_categories() -> Optional[pd.DataFrame]:
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/coins/categories", timeout=25)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        cols = ["id","name","market_cap","market_cap_change_24h","top_3_coins","volume_24h"]
        df = df[[c for c in cols if c in df.columns]]
        def preview(links):
            if isinstance(links, list):
                return ", ".join(links[:3])
            return ""
        df["top_3_preview"] = df["top_3_coins"].apply(preview)
        df = df.drop(columns=["top_3_coins"], errors="ignore")
        return df.sort_values("market_cap_change_24h", ascending=False)
    except Exception as e:
        st.warning(f"CoinGecko categories fetch failed: {e}")
        return None

@st.cache_data(ttl=600)
def get_altcoin_season_index(api_key: Optional[str]) -> Optional[dict]:
    if not api_key:
        return None
    try:
        headers = {"coinglassSecret": api_key}
        resp = requests.get("https://open-api.coinglass.com/api/pro/v1/altcoin/season", headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"CoinGlass Altcoin Season Index fetch failed: {e}")
        return None

def rotation_signal(btc_dom: Optional[float], ethbtc: Optional[float]) -> str:
    if btc_dom is None or ethbtc is None:
        return "⏳ Insufficient data for rotation signal."
    if btc_dom > btc_dom_threshold:
        return "🟠 Stay BTC-heavy or defensive (BTC.D high)."
    if btc_dom <= btc_dom_threshold and ethbtc >= ethbtc_bull_threshold:
        return "🟢 Rotate to ETH & Large-Cap Alts."
    if btc_dom <= btc_dom_threshold and ethbtc < ethbtc_bull_threshold:
        return "🟢/🟡 Mixed: BTC.D low but ETH/BTC not strong — focus on selective large/mid-cap narratives."
    return "⏳ Monitor conditions."

# ------------------------------
# OVERVIEW
# ------------------------------
st.header("🧭 Overview")
colA, colB, colC = st.columns(3)

fng = get_fng()
if fng:
    colA.metric("Fear & Greed Index", value=fng["value"], delta=fng["classification"])

gl = get_coingecko_global()
if gl and "market_cap_percentage" in gl:
    btc_dom = float(gl["market_cap_percentage"].get("btc", 0.0))
    eth_dom = float(gl["market_cap_percentage"].get("eth", 0.0))
    colB.metric("BTC Dominance", f"{btc_dom:.2f}%")
    colC.metric("ETH Dominance", f"{eth_dom:.2f}%")
else:
    btc_dom = None

ethbtc = get_eth_btc_ratio()
st.caption(f"ETH/BTC: {ethbtc:.5f}" if ethbtc is not None else "ETH/BTC: unavailable")

sig = rotation_signal(btc_dom, ethbtc)
st.success(f"**Rotation Signal:** {sig}")

st.markdown("---")

# ------------------------------
# TABS
# ------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Cycle Top Signals", 
    "🏛 Market Structure", 
    "🔥 Narratives", 
    "🧺 Watchlist Buckets", 
    "🧩 How to Use"
])

with tab1:
    st.subheader("Cycle Top Signals (Embeds)")
    st.caption("Live views from public sources. If they fail to load, open the links in a new tab.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Pi Cycle Top Indicator**")
        st.components.v1.iframe("https://www.bitcoinmagazinepro.com/charts/pi-cycle-top-indicator/", height=580)
    with c2:
        st.markdown("**MVRV Z-Score**")
        st.components.v1.iframe("https://www.bitcoinmagazinepro.com/charts/mvrv-zscore/", height=580)
    st.markdown("**Google Trends: 'how to buy crypto' (US, all time)**")
    st.components.v1.iframe("https://trends.google.com/trends/explore?date=all&geo=US&q=how%20to%20buy%20crypto&hl=en", height=600)
    st.markdown("**Fear & Greed Index**")
    st.components.v1.iframe("https://alternative.me/crypto/fear-and-greed-index/", height=520)

with tab2:
    st.subheader("Market Structure")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**BTC Dominance (TradingView)**")
        st.components.v1.iframe("https://www.tradingview.com/chart/SpyzxsYP/?symbol=CRYPTOCAP%3ABTC.D", height=520)
    with c2:
        st.markdown("**ETH Dominance (TradingView)**")
        st.components.v1.iframe("https://www.tradingview.com/chart/SpyzxsYP/?symbol=CRYPTOCAP%3AETH.D", height=520)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**BTCUSD (TradingView)**")
        st.components.v1.iframe("https://www.tradingview.com/chart/SpyzxsYP/?symbol=BITSTAMP%3ABTCUSD", height=520)
    with c4:
        st.markdown("**ETH/BTC quick stat**")
        st.metric("ETH/BTC", f"{ethbtc:.5f}" if ethbtc is not None else "unavailable")

    st.markdown("---")
    st.subheader("Altcoin Season Index")
    if alt_season_index_key:
        data = get_altcoin_season_index(alt_season_index_key)
        if data:
            st.json(data)
        else:
            st.info("No data or invalid API key. See 'How to Use' tab for setup.")
    else:
        st.info("Provide a CoinGlass API key in the sidebar to fetch the Altcoin Season Index automatically.")

with tab3:
    st.subheader("Narratives")
    st.caption("CoinGecko Categories (24h change, public API). Sort to find the hottest sectors.")
    cats = get_coingecko_categories()
    if cats is not None and not cats.empty:
        st.dataframe(
            cats.rename(columns={
                "name":"Category",
                "market_cap":"Mkt Cap ($)",
                "market_cap_change_24h":"24h %",
                "volume_24h":"Vol 24h ($)",
                "top_3_preview":"Top 3 Coins (preview)"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Categories unavailable right now. Try again later.")
    st.markdown("**DeFiLlama Narrative Tracker (embed)**")
    st.components.v1.iframe("https://defillama.com/narrative-tracker", height=700)

    st.markdown("**Coin App Rank Bot (X) — sentiment pulses**")
    st.components.v1.iframe("https://x.com/COINAppRankBot", height=700)

with tab4:
    st.subheader("Watchlist Buckets (per your rotation framework)")
    st.caption("Quick-access charts on TradingView for fast context switching.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### L1 / Majors")
        st.markdown("- [SOLUSD (Coinbase)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=COINBASE%3ASOLUSD)")
        st.markdown("- [ETH Dominance](https://www.tradingview.com/chart/SpyzxsYP/?symbol=CRYPTOCAP%3AETH.D)")
        st.markdown("- [BTC Dominance](https://www.tradingview.com/chart/SpyzxsYP/?symbol=CRYPTOCAP%3ABTC.D)")
    with col2:
        st.markdown("### AI / Compute")
        st.markdown("- [RNDRUSD (Gemini)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=GEMINI%3ARNDRUSD)")
        st.markdown("- [TAOUSDT (Binance)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BINANCE%3ATAOUSDT)")
        st.markdown("- [MNTUSDT (Bybit)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BYBIT%3AMNTUSDT)")
        st.markdown("- [CFGUSDT (OKX)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=OKX%3ACFGUSDT)")
        st.markdown("- [TRACUSD (Coinbase)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=COINBASE%3ATRACUSD)")
        st.markdown("- [ARKMUSDT (Binance)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BINANCE%3AARKMUSDT)")
        st.markdown("- [BEAMUSDT (Bybit)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BYBIT%3ABEAMUSDT)")
        st.markdown("- [XAIUSDT (Binance)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BINANCE%3AXAIUSDT)")
    with col3:
        st.markdown("### RWA / Stablecoin Infra & Others")
        st.markdown("- [ONDOUSDT (Bybit)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BYBIT%3AONDOUSDT)")
        st.markdown("- [IMXUSDT (Binance)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BINANCE%3AIMXUSDT)")
        st.markdown("- [TIAUSDT (Binance)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BINANCE%3ATIAUSDT)")
        st.markdown("- [SUIUSDT (Binance)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BINANCE%3ASUIUSDT)")
        st.markdown("- [DEGENUSDT (Bybit)](https://www.tradingview.com/chart/SpyzxsYP/?symbol=BYBIT%3ADEGENUSDT)")

with tab5:
    st.subheader("How to Use This Dashboard")
    st.markdown("""
**Rotation Playbook (simplified):**
- **BTC Phase**: BTC Dominance rising or > threshold → Stay BTC-heavy/defensive.
- **ETH Phase**: BTC Dominance falls **below** threshold AND ETH/BTC **above** bull threshold → Rotate to **ETH & Large-Cap Alts**.
- **Alt Season**: BTC Dominance stays low and ETH/BTC trends up → Add **mid/small-cap narratives** (AI, RWA, etc.).

**What’s included (no API keys needed):**
- Pi Cycle Top (embed)
- MVRV Z-Score (embed)
- Fear & Greed Index (API)
- Google Trends embed for "how to buy crypto"
- BTC & ETH Dominance (CoinGecko global API)
- ETH/BTC quick stat (CoinGecko API)
- CoinGecko Categories table (public API)
- DeFiLlama Narrative Tracker (embed)
- TradingView quick-access links for your watchlist buckets

**Optional (needs API keys later):**
- CoinGlass Altcoin Season Index (enter key in the sidebar when you have it)

**Tips:**
- Adjust the thresholds in the sidebar to fit your risk appetite.
- Use the Narratives tab to spot hot categories (sorting by 24h%). 
- Confirm timing using Cycle Top Signals + BTC.D behavior, then execute rotations.
    """)

st.caption("Built for Brandon’s strategy • Public-Data Edition v1.0")
