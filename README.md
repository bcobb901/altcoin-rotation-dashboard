# Altcoin Season Rotation Dashboard (Public-Data Edition)

A Streamlit dashboard that pulls together cycle-top signals, BTC/ETH dominance, ETH/BTC, narratives, and your watchlist — using **only public data sources** so it runs without API keys.

## What’s Included (no keys needed)
- **Pi Cycle Top** (embed)
- **MVRV Z-Score** (embed)
- **Fear & Greed Index** via alternative.me
- **Google Trends** embed for "how to buy crypto"
- **BTC & ETH Dominance** via CoinGecko global API
- **ETH/BTC** via CoinGecko simple price
- **CoinGecko Categories** (24h change) table
- **DeFiLlama Narrative Tracker** (embed)
- **TradingView** quick links for your watchlist (SOL, SUI, RNDR, ONDO, TAO, etc.)

## Optional (later, with keys)
- **CoinGlass Altcoin Season Index** — add your `coinglassSecret` key in the app sidebar when you have it.

---

## 🚀 Deploy to Streamlit Community Cloud (no coding)

1) **Create a new GitHub repo** (private is fine).  
   Upload these three files:
   - `app.py`
   - `requirements.txt`
   - `README.md`

2) Go to **https://share.streamlit.io** and sign in with GitHub.  
3) Click **New app** → select your repo → branch → set **Main file path** to `app.py`.  
4) Click **Deploy**. That’s it — you’ll get a shareable link.

### Local run (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Adding the CoinGlass API key later
- Sign up and get a key (look for `coinglassSecret`) from the CoinGlass API docs.
- Open the deployed app → enter the key in the sidebar field to enable the Altcoin Season Index panel.
