import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import os
import json
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG — mobile-first
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ScalpEdge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  :root {
    --bg: #ffffff;
    --surface: #f8fafc;
    --surface2: #f1f5f9;
    --border: #e2e8f0;
    --accent: #0ea5e9;
    --accent2: #f59e0b;
    --up: #16a34a;
    --down: #dc2626;
    --text: #0f172a;
    --muted: #64748b;
    --bb1: rgba(234,179,8,0.9);
    --bb2: rgba(234,88,12,0.9);
    --bb3: rgba(220,38,38,0.9);
  }

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }

  .stApp { background-color: var(--bg) !important; }

  /* Header */
  .app-header {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdf4 100%);
    border-bottom: 2px solid var(--border);
    padding: 1rem 1.5rem 0.8rem;
    margin: -1rem -1rem 1.5rem -1rem;
  }
  .app-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #0ea5e9;
    letter-spacing: -0.5px;
    margin: 0;
  }
  .app-subtitle {
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
  }

  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
  }
  .card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  /* Inputs */
  .stTextInput input, .stSelectbox select, .stNumberInput input {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
  }
  .stTextInput input:focus, .stSelectbox select:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(14,165,233,0.15) !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.3) !important;
  }

  /* Direction buttons */
  .dir-btn-up button { background: linear-gradient(135deg, #16a34a, #15803d) !important; color: #ffffff !important; }
  .dir-btn-down button { background: linear-gradient(135deg, #dc2626, #b91c1c) !important; color: #ffffff !important; }
  .dir-btn-side button { background: linear-gradient(135deg, #f59e0b, #d97706) !important; color: #ffffff !important; }

  /* Metric cards */
  .metric-row {
    display: flex;
    gap: 8px;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }
  .metric-box {
    flex: 1;
    min-width: 80px;
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    text-align: center;
  }
  .metric-label {
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }
  .metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    font-weight: 700;
    color: #0ea5e9;
    margin-top: 2px;
  }
  .metric-value.up { color: #16a34a; }
  .metric-value.down { color: #dc2626; }

  /* Status badge */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-weight: 600;
  }
  .badge-green { background: rgba(22,163,74,0.1); color: #16a34a; border: 1px solid rgba(22,163,74,0.3); }
  .badge-red { background: rgba(220,38,38,0.1); color: #dc2626; border: 1px solid rgba(220,38,38,0.3); }
  .badge-amber { background: rgba(245,158,11,0.1); color: #d97706; border: 1px solid rgba(245,158,11,0.3); }

  /* Divider */
  .section-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
  }

  /* Hide streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1rem !important; max-width: 100% !important; }

  /* Select boxes */
  div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
  }

  /* Labels */
  .stTextInput label, .stSelectbox label, .stNumberInput label,
  .stDateInput label, .stSlider label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-family: 'JetBrains Mono', monospace !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: var(--muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
  }
  .stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #0ea5e9 !important;
  }

  /* Forecast label */
  .forecast-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    padding: 4px 12px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.5rem;
  }
  .forecast-up { background: rgba(22,163,74,0.1); color: #16a34a; border: 1px solid rgba(22,163,74,0.3); }
  .forecast-down { background: rgba(220,38,38,0.1); color: #dc2626; border: 1px solid rgba(220,38,38,0.3); }
  .forecast-side { background: rgba(245,158,11,0.1); color: #d97706; border: 1px solid rgba(245,158,11,0.3); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-title">⚡ ScalpEdge</div>
  <div class="app-subtitle">Bollinger Band Scalping Tool · Angel One SmartAPI</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PASSWORD GATE — locks the entire app
# ─────────────────────────────────────────────
def _check_password():
    """Returns True only after the correct password is entered.

    Reads the expected password from st.secrets['app_password'].
    If no secret is configured, the gate is bypassed (useful for local dev
    when running without secrets.toml).
    """
    try:
        expected = st.secrets.get("app_password", None)
    except Exception:
        expected = None

    # No password configured → bypass gate (e.g. local dev without secrets)
    if not expected:
        return True

    if st.session_state.get("auth_ok", False):
        return True

    st.markdown(
        '<div class="card" style="max-width:420px; margin:3rem auto;">'
        '<div class="card-title">🔒 PROTECTED APP</div>',
        unsafe_allow_html=True,
    )
    pw = st.text_input("Password", type="password", key="auth_pw_input",
                       label_visibility="collapsed",
                       placeholder="Enter app password")
    if st.button("UNLOCK", key="auth_btn"):
        if pw == expected:
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


_check_password()


# ─────────────────────────────────────────────
# SECRETS LOADER — pulls SmartAPI creds from st.secrets if present
# ─────────────────────────────────────────────
def _load_secrets_creds():
    """Returns dict of credentials from st.secrets, or {} if absent."""
    try:
        if "angel_one" in st.secrets:
            sec = st.secrets["angel_one"]
            return {
                "api_key":   sec.get("api_key", ""),
                "client_id": sec.get("client_id", ""),
                "password":  sec.get("password", ""),
                "totp_key":  sec.get("totp_key", ""),
            }
    except Exception:
        pass
    return {}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

INTERVAL_MAP = {
    "1 min": "ONE_MINUTE",
    "3 min": "THREE_MINUTE",
    "5 min": "FIVE_MINUTE",
    "15 min": "FIFTEEN_MINUTE",
    "30 min": "THIRTY_MINUTE",
    "1 hour": "ONE_HOUR",
    "1 day": "ONE_DAY",
}

SYMBOL_TOKEN_MAP = {
    "NIFTY 50":   ("NSE", "99926000", "NSE"),
    "BANKNIFTY":  ("NSE", "99926009", "NSE"),
    "RELIANCE":   ("NSE", "2885",     "NSE"),
    "INFY":       ("NSE", "1594",     "NSE"),
    "TCS":        ("NSE", "11536",    "NSE"),
    "HDFCBANK":   ("NSE", "1333",     "NSE"),
    "ICICIBANK":  ("NSE", "4963",     "NSE"),
    "SBIN":       ("NSE", "3045",     "NSE"),
    "ADANIENT":   ("NSE", "25",       "NSE"),
    "TATAMOTORS": ("NSE", "3456",     "NSE"),
}

def compute_bollinger_bands(df, period=20):
    df = df.copy()
    df["bb_mid"] = df["close"].rolling(period).mean()
    df["bb_std"] = df["close"].rolling(period).std()
    for dev in [1.5, 2.0, 2.5]:
        tag = str(dev).replace(".", "")
        df[f"bb_upper_{tag}"] = df["bb_mid"] + dev * df["bb_std"]
        df[f"bb_lower_{tag}"] = df["bb_mid"] - dev * df["bb_std"]
    return df


# ═══════════════════════════════════════════════════════════════════════════
#  AL BROOKS PRICE ACTION ENGINE
#  Source: Trading Price Action Trends — Al Brooks (Wiley, 2012)
#  Detects 12 Brooks setups from OHLC bars + 20-EMA only.
# ═══════════════════════════════════════════════════════════════════════════

def _ema(series, n):
    return series.ewm(span=n, adjust=False).mean()


def detect_brooks_signals(df):
    """
    Detect Al Brooks price action signals from OHLC data.
    df expects lowercase columns: open, high, low, close, datetime.
    Returns list of signal dicts. Each dict carries `bar_idx` (int) marking
    which bar the signal fired on — used for chart annotation.
    """
    signals = []
    n = len(df)
    if n < 10:
        return signals

    closes = df["close"].values
    highs  = df["high"].values
    lows   = df["low"].values
    opens  = df["open"].values
    current = closes[-1]

    ema20_series = _ema(df["close"], min(20, n - 1))
    ema20 = ema20_series.iloc[-1]
    ema20_prev = ema20_series.iloc[-2] if n > 2 else ema20
    ema_rising = ema20 > ema20_prev

    def bar_size(i):
        return highs[i] - lows[i]

    def is_bull_bar(i):
        return closes[i] > opens[i]

    def is_bear_bar(i):
        return closes[i] < opens[i]

    def body_pct(i):
        rng = bar_size(i)
        return abs(closes[i] - opens[i]) / rng if rng > 0 else 0

    def is_strong_bar(i, threshold=0.5):
        return body_pct(i) >= threshold

    avg_bar_size = float(np.mean([bar_size(i) for i in range(max(0, n - 20), n)]))
    last_idx = n - 1  # absolute index of the last bar

    # ── 1. INSIDE BAR / ii PATTERN ─────────────────────────────────────────
    if n >= 3:
        ib1 = (highs[-1] <= highs[-2] and lows[-1] >= lows[-2])
        ib2 = (n >= 4 and
               highs[-2] <= highs[-3] and lows[-2] >= lows[-3] and
               highs[-1] <= highs[-2] and lows[-1] >= lows[-2])
        if ib1 or ib2:
            pattern = "ii Pattern" if ib2 else "Inside Bar"
            ib_high = highs[-3] if ib2 else highs[-2]
            ib_low  = lows[-3]  if ib2 else lows[-2]
            conf = 80 if ib2 else 65
            signals.append({
                "name": f"Brooks: {pattern} (Breakout Mode)",
                "signal": "BREAKOUT MODE — BOTH SIDES",
                "direction": "BOTH",
                "color": "#f59e0b",
                "confidence": conf,
                "entry": f"BUY > {ib_high + 0.01:.2f} | SELL < {ib_low - 0.01:.2f}",
                "stop": f"Long: {ib_low - 0.01:.2f} | Short: {ib_high + 0.01:.2f}",
                "target": f"Range × 2 in breakout direction",
                "bar_idx": last_idx,
                "level_entry_up": ib_high + 0.01,
                "level_entry_dn": ib_low - 0.01,
            })

    # ── 2. TWO-BAR REVERSAL ────────────────────────────────────────────────
    if n >= 2:
        b1_bull = is_bull_bar(-2) and is_strong_bar(-2, 0.55)
        b2_bear = is_bear_bar(-1) and is_strong_bar(-1, 0.55)
        b1_bear = is_bear_bar(-2) and is_strong_bar(-2, 0.55)
        b2_bull = is_bull_bar(-1) and is_strong_bar(-1, 0.55)
        has_overlap = min(highs[-1], highs[-2]) > max(lows[-1], lows[-2])

        if b1_bull and b2_bear and has_overlap:
            entry = lows[-1] - 0.01
            stop  = highs[-2] + 0.01
            risk  = stop - entry
            signals.append({
                "name": "Brooks: Two-Bar Reversal (Bearish)",
                "signal": "▼ BEARISH REVERSAL",
                "direction": "SHORT",
                "color": "#dc2626",
                "confidence": 72,
                "entry": f"SELL STOP: {entry:.2f}",
                "stop": f"{stop:.2f}",
                "target": f"T1: 20-EMA | T2: {entry - risk * 2:.2f} (2R)",
                "bar_idx": last_idx,
                "level_entry": entry,
                "level_stop": stop,
                "level_target": entry - risk * 2,
            })
        elif b1_bear and b2_bull and has_overlap:
            entry = highs[-1] + 0.01
            stop  = lows[-2] - 0.01
            risk  = entry - stop
            signals.append({
                "name": "Brooks: Two-Bar Reversal (Bullish)",
                "signal": "▲ BULLISH REVERSAL",
                "direction": "LONG",
                "color": "#16a34a",
                "confidence": 72,
                "entry": f"BUY STOP: {entry:.2f}",
                "stop": f"{stop:.2f}",
                "target": f"T1: 20-EMA = {ema20:.2f} | T2: {entry + risk * 2:.2f} (2R)",
                "bar_idx": last_idx,
                "level_entry": entry,
                "level_stop": stop,
                "level_target": entry + risk * 2,
            })

    # ── 3. MA GAP BAR ──────────────────────────────────────────────────────
    if n >= 5 and ema_rising and current > ema20:
        for i in range(-3, -1):
            if highs[i] < ema20 * 0.999:
                next_i = i + 1
                if next_i < 0 and is_bull_bar(next_i):
                    entry = highs[next_i] + 0.01
                    stop  = lows[i] - 0.01
                    risk  = entry - stop
                    signals.append({
                        "name": "Brooks: MA Gap Bar (Strong Trend Re-Entry)",
                        "signal": "▲▲ STRONG BULL TREND",
                        "direction": "LONG",
                        "color": "#15803d",
                        "confidence": 78,
                        "entry": f"BUY STOP: {entry:.2f}",
                        "stop": f"{stop:.2f}",
                        "target": f"Prior swing high | 2R: {entry + risk * 2:.2f}",
                        "bar_idx": last_idx,
                        "level_entry": entry,
                        "level_stop": stop,
                        "level_target": entry + risk * 2,
                    })
                    break

    # ── 4. HIGH 1 / HIGH 2 PULLBACK ────────────────────────────────────────
    if n >= 6 and current > ema20 and ema_rising:
        pullback_bars = 0
        for i in range(-5, -1):
            if highs[i] < highs[i - 1]:
                pullback_bars += 1
        if pullback_bars >= 2 and highs[-1] > highs[-2] and is_bull_bar(-1):
            attempt = "High 2" if pullback_bars >= 3 else "High 1"
            conf = 75 if pullback_bars >= 3 else 60
            entry = highs[-1] + 0.01
            stop  = lows[-2] - 0.01
            risk  = entry - stop
            signals.append({
                "name": f"Brooks: {attempt} Pullback (Bull Trend Entry)",
                "signal": "▲ BULL TREND PULLBACK",
                "direction": "LONG",
                "color": "#16a34a",
                "confidence": conf,
                "entry": f"BUY STOP: {entry:.2f}",
                "stop": f"{stop:.2f}",
                "target": f"Prior swing high | 2R: {entry + risk * 2:.2f}",
                "bar_idx": last_idx,
                "level_entry": entry,
                "level_stop": stop,
                "level_target": entry + risk * 2,
            })

    # ── 5. MEASURED MOVE PROJECTION ────────────────────────────────────────
    if n >= 15:
        try:
            from scipy.signal import argrelextrema
            h_idx = argrelextrema(highs, np.greater_equal, order=3)[0]
            l_idx = argrelextrema(lows,  np.less_equal,    order=3)[0]
            if len(l_idx) >= 2 and len(h_idx) >= 1:
                l1, h1, l2 = l_idx[-2], h_idx[-1], l_idx[-1]
                if l1 < h1 > l2:
                    leg1 = highs[h1] - lows[l1]
                    corr = (highs[h1] - lows[l2]) / highs[h1] * 100
                    if 25 <= corr <= 65 and leg1 > 0:
                        mm_target = lows[l2] + leg1
                        signals.append({
                            "name": "Brooks: Measured Move Projection",
                            "signal": "▲ MEASURED MOVE BULLISH",
                            "direction": "LONG",
                            "color": "#0ea5e9",
                            "confidence": 70,
                            "entry": f"BUY near {lows[l2]:.2f}",
                            "stop": f"{lows[l2] * 0.99:.2f}",
                            "target": f"{mm_target:.2f} (Leg1={leg1:.2f}, 75% hit rate)",
                            "bar_idx": last_idx,
                            "level_target": mm_target,
                            "level_entry": lows[l2],
                        })
        except Exception:
            pass

    # ── 6. TREND FROM THE OPEN ─────────────────────────────────────────────
    if n >= 5:
        first5_bull = all(is_bull_bar(i) for i in range(min(5, n)))
        first5_bear = all(is_bear_bar(i) for i in range(min(5, n)))
        first5_sizes = [bar_size(i) for i in range(min(5, n))]
        all_large = all(s > avg_bar_size * 0.6 for s in first5_sizes)
        if (first5_bull or first5_bear) and all_large:
            direction = "BULL" if first5_bull else "BEAR"
            signals.append({
                "name": f"Brooks: Trend from the Open ({direction})",
                "signal": f"{'▲▲ STRONG BULL' if first5_bull else '▼▼ STRONG BEAR'} TREND DAY",
                "direction": "LONG" if first5_bull else "SHORT",
                "color": "#16a34a" if first5_bull else "#dc2626",
                "confidence": 80,
                "entry": "Any with-trend pullback",
                "stop": "Below pullback low (bull) / above pullback high (bear)",
                "target": "1× avg bar size scalp | Hold 50% all day",
                "bar_idx": min(4, n - 1),
            })

    # ── 7. WEDGE REVERSAL ──────────────────────────────────────────────────
    if n >= 12:
        try:
            from scipy.signal import argrelextrema
            h_idx = argrelextrema(highs, np.greater_equal, order=3)[0]
            l_idx = argrelextrema(lows,  np.less_equal,    order=3)[0]

            if len(h_idx) >= 3:
                h1, h2, h3 = highs[h_idx[-3]], highs[h_idx[-2]], highs[h_idx[-1]]
                if h1 > h2 > h3 * 1.001:
                    d1, d2 = h1 - h2, h2 - h3
                    if d1 > 0 and d2 > 0 and d2 < d1 * 1.5:
                        entry = lows[-1] - 0.01
                        stop  = h3 + 0.01
                        signals.append({
                            "name": "Brooks: Wedge Reversal (Bearish Top)",
                            "signal": "▼ THREE-PUSH EXHAUSTION TOP",
                            "direction": "SHORT",
                            "color": "#dc2626",
                            "confidence": 70,
                            "entry": f"SELL STOP: {entry:.2f}",
                            "stop": f"{stop:.2f}",
                            "target": f"T1: {lows[h_idx[-3]]:.2f} (wedge start)",
                            "bar_idx": last_idx,
                            "level_entry": entry,
                            "level_stop": stop,
                            "level_target": lows[h_idx[-3]],
                        })

            if len(l_idx) >= 3:
                l1, l2, l3 = lows[l_idx[-3]], lows[l_idx[-2]], lows[l_idx[-1]]
                if l1 < l2 < l3 * 0.999:
                    d1, d2 = l2 - l1, l3 - l2
                    if d1 > 0 and d2 > 0 and d2 < d1 * 1.5:
                        entry = highs[-1] + 0.01
                        stop  = l3 - 0.01
                        signals.append({
                            "name": "Brooks: Wedge Reversal (Bullish Bottom)",
                            "signal": "▲ THREE-PUSH EXHAUSTION BOTTOM",
                            "direction": "LONG",
                            "color": "#16a34a",
                            "confidence": 70,
                            "entry": f"BUY STOP: {entry:.2f}",
                            "stop": f"{stop:.2f}",
                            "target": f"T1: {highs[l_idx[-3]]:.2f} (wedge start)",
                            "bar_idx": last_idx,
                            "level_entry": entry,
                            "level_stop": stop,
                            "level_target": highs[l_idx[-3]],
                        })
        except Exception:
            pass

    # ── 8. FAILED BREAKOUT ─────────────────────────────────────────────────
    if n >= 5:
        try:
            from scipy.signal import argrelextrema
            h_idx = argrelextrema(highs, np.greater_equal, order=5)[0]
            l_idx = argrelextrema(lows,  np.less_equal,    order=5)[0]

            if len(h_idx) >= 2:
                prior_high = highs[h_idx[-2]]
                for i in range(-4, -1):
                    if highs[i] > prior_high and closes[i] < prior_high:
                        entry = lows[-1] - 0.01
                        stop  = highs[i] + 0.01
                        risk  = stop - entry
                        signals.append({
                            "name": "Brooks: Failed Breakout (Bearish)",
                            "signal": "▼ FAILED BULL BREAKOUT",
                            "direction": "SHORT",
                            "color": "#dc2626",
                            "confidence": 73,
                            "entry": f"SELL STOP: {entry:.2f}",
                            "stop": f"{stop:.2f}",
                            "target": f"2R: {entry - risk * 2:.2f}",
                            "bar_idx": last_idx,
                            "level_entry": entry,
                            "level_stop": stop,
                            "level_target": entry - risk * 2,
                        })
                        break

            if len(l_idx) >= 2:
                prior_low = lows[l_idx[-2]]
                for i in range(-4, -1):
                    if lows[i] < prior_low and closes[i] > prior_low:
                        entry = highs[-1] + 0.01
                        stop  = lows[i] - 0.01
                        risk  = entry - stop
                        signals.append({
                            "name": "Brooks: Failed Breakout (Bullish)",
                            "signal": "▲ FAILED BEAR BREAKOUT",
                            "direction": "LONG",
                            "color": "#16a34a",
                            "confidence": 73,
                            "entry": f"BUY STOP: {entry:.2f}",
                            "stop": f"{stop:.2f}",
                            "target": f"2R: {entry + risk * 2:.2f}",
                            "bar_idx": last_idx,
                            "level_entry": entry,
                            "level_stop": stop,
                            "level_target": entry + risk * 2,
                        })
                        break
        except Exception:
            pass

    # ── 9. BREAKOUT PULLBACK ───────────────────────────────────────────────
    if n >= 10:
        try:
            from scipy.signal import argrelextrema
            h_idx = argrelextrema(highs, np.greater_equal, order=4)[0]
            if len(h_idx) >= 2:
                prior_swing_high = highs[h_idx[-2]]
                bk_idx = h_idx[-1]
                if (highs[bk_idx] > prior_swing_high and
                        closes[bk_idx] > prior_swing_high and
                        n - bk_idx <= 6):
                    pullback_bars = n - bk_idx - 1
                    if 1 <= pullback_bars <= 5:
                        pb_lows = [lows[bk_idx + j] for j in range(1, pullback_bars + 1)]
                        pb_sizes = [bar_size(bk_idx + j) for j in range(1, pullback_bars + 1)]
                        avg_pb = float(np.mean(pb_sizes)) if pb_sizes else avg_bar_size
                        tight = avg_pb < avg_bar_size * 1.2
                        holds = min(pb_lows) > prior_swing_high * 0.997
                        if tight and holds:
                            entry = highs[-1] + 0.01
                            stop  = min(pb_lows) - 0.01
                            bk_ht = closes[bk_idx] - lows[bk_idx]
                            signals.append({
                                "name": "Brooks: Breakout Pullback (Long)",
                                "signal": "▲ BREAKOUT PULLBACK LONG",
                                "direction": "LONG",
                                "color": "#15803d",
                                "confidence": 80,
                                "entry": f"BUY STOP: {entry:.2f}",
                                "stop": f"{stop:.2f}",
                                "target": f"T1: {entry + bk_ht:.2f} | T2: {entry + bk_ht * 2:.2f}",
                                "bar_idx": last_idx,
                                "level_entry": entry,
                                "level_stop": stop,
                                "level_target": entry + bk_ht * 2,
                            })
        except Exception:
            pass

    # ── 10. SPIKE AND CHANNEL ──────────────────────────────────────────────
    if n >= 15:
        spike_len = 0
        spike_dir = None
        for i in range(-8, -1):
            if is_bull_bar(i) and is_strong_bar(i, 0.6) and bar_size(i) > avg_bar_size:
                if spike_dir is None or spike_dir == "bull":
                    spike_dir = "bull"
                    spike_len += 1
                else:
                    break
            elif is_bear_bar(i) and is_strong_bar(i, 0.6) and bar_size(i) > avg_bar_size:
                if spike_dir is None or spike_dir == "bear":
                    spike_dir = "bear"
                    spike_len += 1
                else:
                    break
            else:
                if spike_len >= 2:
                    break
                spike_len = 0
                spike_dir = None

        if spike_len >= 2 and spike_dir:
            channel_bars = [i for i in range(-4, 0) if bar_size(i) < avg_bar_size * 1.1]
            if len(channel_bars) >= 2:
                signals.append({
                    "name": f"Brooks: Spike and Channel ({'Bull' if spike_dir == 'bull' else 'Bear'})",
                    "signal": f"{'▲ BULL' if spike_dir == 'bull' else '▼ BEAR'} SPIKE AND CHANNEL",
                    "direction": "LONG" if spike_dir == "bull" else "SHORT",
                    "color": "#16a34a" if spike_dir == "bull" else "#dc2626",
                    "confidence": 68,
                    "entry": "Buy pullback to channel line (bull) / sell rally (bear)",
                    "stop": "Below signal bar low in channel",
                    "target": "Prior swing | spike-height measured move",
                    "bar_idx": last_idx,
                })

    # ── 11. TREND LINE BREAK + LOWER HIGH ──────────────────────────────────
    if n >= 20:
        try:
            from scipy.signal import argrelextrema
            h_idx = argrelextrema(highs, np.greater_equal, order=4)[0]
            l_idx = argrelextrema(lows,  np.less_equal,    order=4)[0]

            if len(h_idx) >= 3 and len(l_idx) >= 2:
                sl1, sl2 = l_idx[-2], l_idx[-1]
                if sl2 > sl1 and lows[sl2] > lows[sl1]:
                    slope = (lows[sl2] - lows[sl1]) / (sl2 - sl1)
                    tl_current = lows[sl2] + slope * (n - 1 - sl2)
                    if closes[-1] < tl_current:
                        last_h, prior_h = highs[h_idx[-1]], highs[h_idx[-2]]
                        if last_h < prior_h:
                            entry = lows[-1] - 0.01
                            stop  = last_h + 0.01
                            signals.append({
                                "name": "Brooks: Trend Line Break + Lower High",
                                "signal": "▼▼ MAJOR REVERSAL SIGNAL",
                                "direction": "SHORT",
                                "color": "#b91c1c",
                                "confidence": 75,
                                "entry": f"SELL STOP: {entry:.2f}",
                                "stop": f"{stop:.2f}",
                                "target": f"T1: {lows[l_idx[-1]]:.2f} | T2: {entry - (prior_h - last_h) * 2:.2f}",
                                "bar_idx": last_idx,
                                "level_entry": entry,
                                "level_stop": stop,
                                "level_target": lows[l_idx[-1]],
                            })
        except Exception:
            pass

    # ── 12. FINAL FLAG ─────────────────────────────────────────────────────
    if n >= 20:
        above_ema_count = sum(1 for i in range(-15, -5) if closes[i] > ema20_series.iloc[i])
        recent_sizes = [bar_size(i) for i in range(-6, 0)]
        tight_recent = all(s < avg_bar_size * 0.8 for s in recent_sizes)
        recent_high = max(highs[i] for i in range(-6, 0))
        recent_low  = min(lows[i]  for i in range(-6, 0))
        flag_range  = recent_high - recent_low

        if above_ema_count >= 8 and tight_recent:
            failed = any(highs[i] > recent_high * 1.001 and closes[i] < recent_high
                         for i in range(-4, 0))
            if failed:
                entry = recent_low - 0.01
                stop  = recent_high + 0.01
                signals.append({
                    "name": "Brooks: Final Flag (Bearish Reversal)",
                    "signal": "▼▼ FINAL FLAG — MAJOR TOP",
                    "direction": "SHORT",
                    "color": "#b91c1c",
                    "confidence": 72,
                    "entry": f"SELL STOP: {entry:.2f}",
                    "stop": f"{stop:.2f}",
                    "target": f"Flag range × 3: {entry - flag_range * 3:.2f}",
                    "bar_idx": last_idx,
                    "level_entry": entry,
                    "level_stop": stop,
                    "level_target": entry - flag_range * 3,
                })

    signals.sort(key=lambda x: x["confidence"], reverse=True)
    return signals


def forecast_candles(df, direction, n=15, period=20):
    """
    Project next n candles based on direction bias + BB state.
    Returns a DataFrame with forecast OHLC + BB bands.
    """
    last = df.iloc[-1]
    last_close = last["close"]
    last_mid = last["bb_mid"]
    last_std = last["bb_std"]

    # BB width trend (squeeze or expansion)
    recent_std = df["bb_std"].tail(10)
    std_slope = (recent_std.iloc[-1] - recent_std.iloc[0]) / 10

    # Momentum
    price_slope = (df["close"].iloc[-1] - df["close"].iloc[-5]) / 5

    # Direction multiplier
    if direction == "UP":
        drift = abs(price_slope) * 0.7 + 0.05 * last_std
        std_trend = std_slope * 0.5 + 0.002 * last_std
        candle_bias = 0.6  # 60% chance of green candle
    elif direction == "DOWN":
        drift = -(abs(price_slope) * 0.7 + 0.05 * last_std)
        std_trend = std_slope * 0.5 + 0.002 * last_std
        candle_bias = 0.35
    else:  # SIDEWAYS
        drift = price_slope * 0.1
        std_trend = -abs(std_slope) * 0.3  # squeeze
        candle_bias = 0.5

    forecasts = []
    cur_close = last_close
    cur_mid = last_mid
    cur_std = last_std

    # Build time index
    last_time = pd.to_datetime(df["datetime"].iloc[-1])
    time_delta = pd.to_datetime(df["datetime"].iloc[-1]) - pd.to_datetime(df["datetime"].iloc[-2])

    for i in range(1, n + 1):
        noise = np.random.normal(0, last_std * 0.15)
        cur_close = cur_close + drift + noise

        # OHLC construction
        candle_range = last_std * np.random.uniform(0.3, 0.7)
        if np.random.random() < candle_bias:
            open_ = cur_close - candle_range * np.random.uniform(0.3, 0.7)
            close_ = cur_close
        else:
            open_ = cur_close + candle_range * np.random.uniform(0.3, 0.7)
            close_ = cur_close

        high_ = max(open_, close_) + candle_range * np.random.uniform(0.1, 0.4)
        low_  = min(open_, close_) - candle_range * np.random.uniform(0.1, 0.4)

        # Update BB state
        cur_std = max(cur_std + std_trend + np.random.normal(0, abs(std_slope) * 0.1), last_std * 0.3)
        cur_mid = cur_mid + drift * 0.8

        row = {
            "datetime": last_time + time_delta * i,
            "open": round(open_, 2),
            "high": round(high_, 2),
            "low":  round(low_,  2),
            "close": round(close_, 2),
            "volume": 0,
            "bb_mid": round(cur_mid, 2),
            "bb_std": round(cur_std, 2),
            "forecast": True,
        }
        for dev in [1.5, 2.0, 2.5]:
            tag = str(dev).replace(".", "")
            row[f"bb_upper_{tag}"] = round(cur_mid + dev * cur_std, 2)
            row[f"bb_lower_{tag}"] = round(cur_mid - dev * cur_std, 2)
        forecasts.append(row)

    return pd.DataFrame(forecasts)

def build_chart(df, forecast_df=None, direction=None):
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.8, 0.2],
        vertical_spacing=0.03,
    )

    # Candlesticks — historical
    fig.add_trace(go.Candlestick(
        x=df["datetime"],
        open=df["open"], high=df["high"],
        low=df["low"],   close=df["close"],
        name="Price",
        increasing_line_color="#16a34a",
        decreasing_line_color="#dc2626",
        increasing_fillcolor="#16a34a",
        decreasing_fillcolor="#dc2626",
    ), row=1, col=1)

    # BB bands — historical
    bb_colors = {
        "15": ("rgba(255,215,0,0.8)",  "rgba(255,215,0,0.05)"),
        "20": ("rgba(255,140,0,0.8)",  "rgba(255,140,0,0.05)"),
        "25": ("rgba(255,80,60,0.8)",  "rgba(255,80,60,0.05)"),
    }
    bb_labels = {"15": "BB 1.5σ", "20": "BB 2.0σ", "25": "BB 2.5σ"}

    for tag, (color, fill) in bb_colors.items():
        dev_label = bb_labels[tag]
        fig.add_trace(go.Scatter(
            x=df["datetime"], y=df[f"bb_upper_{tag}"],
            name=f"{dev_label} Upper",
            line=dict(color=color, width=1.2, dash="dot"),
            showlegend=True,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["datetime"], y=df[f"bb_lower_{tag}"],
            name=f"{dev_label} Lower",
            line=dict(color=color, width=1.2, dash="dot"),
            fill="tonexty" if tag == "15" else None,
            fillcolor=fill,
            showlegend=False,
        ), row=1, col=1)

    # BB midline
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["bb_mid"],
        name="BB Mid (20 SMA)",
        line=dict(color="rgba(100,180,255,0.7)", width=1.5),
    ), row=1, col=1)

    # Forecast candles
    if forecast_df is not None and len(forecast_df) > 0:
        dir_color_up   = "#00c896"
        dir_color_down = "#ff4d6d"
        dir_color_side = "#f59e0b"

        if direction == "UP":
            fc_color = dir_color_up
        elif direction == "DOWN":
            fc_color = dir_color_down
        else:
            fc_color = dir_color_side

        # Vertical separator
        sep_time = df["datetime"].iloc[-1]
        fig.add_vline(
            x=sep_time, line_dash="dash",
            line_color="rgba(255,255,255,0.2)", line_width=1,
        )

        fig.add_trace(go.Candlestick(
            x=forecast_df["datetime"],
            open=forecast_df["open"], high=forecast_df["high"],
            low=forecast_df["low"],   close=forecast_df["close"],
            name="Forecast",
            increasing_line_color=fc_color,
            decreasing_line_color=fc_color,
            increasing_fillcolor=f"rgba({','.join(str(int(fc_color.lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.4)",
            decreasing_fillcolor="rgba(80,80,80,0.3)",
            opacity=0.7,
        ), row=1, col=1)

        # Forecast BB bands
        for tag, (color, _) in bb_colors.items():
            fig.add_trace(go.Scatter(
                x=forecast_df["datetime"], y=forecast_df[f"bb_upper_{tag}"],
                line=dict(color=color, width=1, dash="longdash"),
                showlegend=False, opacity=0.5,
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=forecast_df["datetime"], y=forecast_df[f"bb_lower_{tag}"],
                line=dict(color=color, width=1, dash="longdash"),
                showlegend=False, opacity=0.5,
            ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=forecast_df["datetime"], y=forecast_df["bb_mid"],
            line=dict(color="rgba(100,180,255,0.4)", width=1.2, dash="longdash"),
            showlegend=False,
        ), row=1, col=1)

    # Volume bars
    colors = ["#16a34a" if c >= o else "#dc2626"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df["datetime"], y=df["volume"],
        name="Volume",
        marker_color=colors,
        opacity=0.6,
    ), row=2, col=1)

    # Layout
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        font=dict(family="JetBrains Mono", color="#334155", size=10),
        margin=dict(l=8, r=8, t=10, b=8),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor="rgba(248,250,252,0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(size=9, color="#334155"),
            x=0.01, y=0.99,
        ),
        height=550,
    )
    fig.update_xaxes(
        gridcolor="#e2e8f0", showgrid=True,
        tickfont=dict(size=9, color="#64748b"),
    )
    fig.update_yaxes(
        gridcolor="#e2e8f0", showgrid=True,
        tickfont=dict(size=9, color="#64748b"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────
#  BROOKS LIVE — CHART BUILDER
# ─────────────────────────────────────────────────────────────────────────

def build_brooks_chart(df, signals):
    """
    Candlestick chart with 20-EMA + per-signal entry/stop/target horizontal
    rays and triangular markers at the bar where each signal fired.
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.85, 0.15],
        vertical_spacing=0.03,
    )

    # Candles
    fig.add_trace(go.Candlestick(
        x=df["datetime"],
        open=df["open"], high=df["high"],
        low=df["low"],   close=df["close"],
        name="Price",
        increasing_line_color="#16a34a",
        decreasing_line_color="#dc2626",
        increasing_fillcolor="#16a34a",
        decreasing_fillcolor="#dc2626",
    ), row=1, col=1)

    # 20-EMA
    ema20 = _ema(df["close"], 20)
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=ema20,
        name="20 EMA",
        line=dict(color="rgba(14,165,233,0.85)", width=1.5),
    ), row=1, col=1)

    # Signal annotations: marker + level rays
    if len(df) > 0:
        x_start = df["datetime"].iloc[0]
        x_end   = df["datetime"].iloc[-1]
        # Extend rays a bit beyond last candle
        time_step = (df["datetime"].iloc[-1] - df["datetime"].iloc[-2]) if len(df) >= 2 else timedelta(minutes=5)
        x_extend = x_end + time_step * 5

        for sig in signals:
            bar_idx = sig.get("bar_idx", len(df) - 1)
            if bar_idx >= len(df):
                bar_idx = len(df) - 1
            x_bar = df["datetime"].iloc[bar_idx]
            y_bar_high = df["high"].iloc[bar_idx]
            y_bar_low  = df["low"].iloc[bar_idx]
            direction = sig.get("direction", "BOTH")
            color = sig.get("color", "#0ea5e9")

            # Marker triangle above/below the bar
            if direction == "LONG":
                marker_y = y_bar_low * 0.998
                marker_symbol = "triangle-up"
            elif direction == "SHORT":
                marker_y = y_bar_high * 1.002
                marker_symbol = "triangle-down"
            else:  # BOTH
                marker_y = y_bar_high * 1.002
                marker_symbol = "diamond"

            fig.add_trace(go.Scatter(
                x=[x_bar],
                y=[marker_y],
                mode="markers+text",
                marker=dict(symbol=marker_symbol, size=14, color=color,
                            line=dict(color="white", width=1)),
                text=[sig.get("signal", "")[:30]],
                textposition="top center" if direction != "LONG" else "bottom center",
                textfont=dict(size=9, color=color, family="JetBrains Mono"),
                name=sig["name"],
                hovertext=(
                    f"<b>{sig['name']}</b><br>"
                    f"Conf: {sig['confidence']}%<br>"
                    f"Entry: {sig.get('entry', '-')}<br>"
                    f"Stop: {sig.get('stop', '-')}<br>"
                    f"Target: {sig.get('target', '-')}"
                ),
                hoverinfo="text",
                showlegend=False,
            ), row=1, col=1)

            # Level rays (entry, stop, target)
            for level_key, dash, label_color in [
                ("level_entry",  "solid", color),
                ("level_stop",   "dot",   "#dc2626"),
                ("level_target", "dash",  "#0ea5e9"),
            ]:
                lv = sig.get(level_key)
                if lv is not None:
                    fig.add_trace(go.Scatter(
                        x=[x_bar, x_extend],
                        y=[lv, lv],
                        mode="lines",
                        line=dict(color=label_color, width=1, dash=dash),
                        opacity=0.55,
                        showlegend=False,
                        hoverinfo="skip",
                    ), row=1, col=1)

            # Inside-bar/ii dual-side levels
            for key in ("level_entry_up", "level_entry_dn"):
                lv = sig.get(key)
                if lv is not None:
                    fig.add_trace(go.Scatter(
                        x=[x_bar, x_extend],
                        y=[lv, lv],
                        mode="lines",
                        line=dict(color=color, width=1, dash="solid"),
                        opacity=0.5,
                        showlegend=False,
                        hoverinfo="skip",
                    ), row=1, col=1)

    # Volume bars
    if "volume" in df.columns:
        vol_colors = ["#16a34a" if c >= o else "#dc2626"
                      for c, o in zip(df["close"], df["open"])]
        fig.add_trace(go.Bar(
            x=df["datetime"], y=df["volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.55,
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        font=dict(family="JetBrains Mono", color="#334155", size=10),
        margin=dict(l=8, r=8, t=10, b=8),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor="rgba(248,250,252,0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(size=9, color="#334155"),
            x=0.01, y=0.99,
        ),
        height=600,
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="#e2e8f0", showgrid=True,
                     tickfont=dict(size=9, color="#64748b"))
    fig.update_yaxes(gridcolor="#e2e8f0", showgrid=True,
                     tickfont=dict(size=9, color="#64748b"))
    return fig


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📡  FETCH DATA",
    "📊  CHART & FORECAST",
    "🎯  BROOKS LIVE",
])

# ══════════════════════════════════════════════
# TAB 1 — DATA FETCHER
# ══════════════════════════════════════════════
with tab1:
    # ── Credentials: prefer st.secrets, fall back to manual entry ────────
    saved = _load_secrets_creds()
    creds_from_secrets = bool(saved.get("api_key"))

    st.markdown('<div class="card"><div class="card-title">🔐 API CREDENTIALS</div>', unsafe_allow_html=True)

    if creds_from_secrets:
        st.markdown(
            '<span class="badge badge-green">✓ CREDENTIALS LOADED FROM SECRETS</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='margin-top:8px; padding:8px 10px; background:#f0fdf4;"
            " border:1px solid #86efac; border-radius:8px;"
            " font-size:0.68rem; color:#15803d; font-family:JetBrains Mono,monospace;"
            " letter-spacing:0.5px;'>"
            "🔒 Credentials are encrypted in Streamlit Cloud Secrets. "
            "Fields below are read-only previews."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        api_key   = st.text_input(
            "API Key", type="password",
            placeholder="Your SmartAPI key",
            value=saved.get("api_key", ""),
            disabled=creds_from_secrets,
        )
        client_id = st.text_input(
            "Client ID",
            placeholder="Angel One client ID",
            value=saved.get("client_id", ""),
            disabled=creds_from_secrets,
        )
    with col2:
        password  = st.text_input(
            "Password", type="password",
            placeholder="Trading password",
            value=saved.get("password", ""),
            disabled=creds_from_secrets,
        )
        totp_key  = st.text_input(
            "TOTP Secret", type="password",
            placeholder="Base32 TOTP key",
            value=saved.get("totp_key", ""),
            disabled=creds_from_secrets,
        )

    if not creds_from_secrets:
        st.markdown(
            "<div style='margin-top:8px; padding:8px 10px; background:#fffbeb;"
            " border:1px solid #fde68a; border-radius:8px;"
            " font-size:0.68rem; color:#92400e; font-family:JetBrains Mono,monospace;"
            " letter-spacing:0.5px;'>"
            "⚠ No secrets configured. Enter credentials manually for this session "
            "(nothing is saved to disk). For cloud deployment, add an [angel_one] "
            "section to your Streamlit secrets."
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ── LOGIN BUTTON + STATUS ────────────────
    is_logged_in = st.session_state.get("logged_in", False)
    login_user   = st.session_state.get("login_user", "")

    lcol1, lcol2 = st.columns([1, 1])
    with lcol1:
        if st.button("🔑  LOGIN TO ANGEL ONE", key="btn_login", disabled=is_logged_in):
            if not all([api_key, client_id, password, totp_key]):
                st.error("Fill all credential fields first.")
            else:
                with st.spinner("Logging in..."):
                    try:
                        import pyotp
                        from SmartApi import SmartConnect
                        totp_code = pyotp.TOTP(totp_key).now()
                        obj       = SmartConnect(api_key=api_key)
                        resp      = obj.generateSession(client_id, password, totp_code)
                        if resp.get("status"):
                            st.session_state["logged_in"]    = True
                            st.session_state["login_user"]   = client_id
                            st.session_state["smart_obj"]    = obj
                            st.session_state["api_key_used"] = api_key
                            st.rerun()
                        else:
                            st.error(f"Login failed: {resp.get('message', 'Unknown error')}")
                    except ImportError:
                        st.error("Run: pip install smartapi-python pyotp")
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
    with lcol2:
        if is_logged_in:
            if st.button("🚪  LOGOUT", key="btn_logout"):
                st.session_state["logged_in"]  = False
                st.session_state["login_user"] = ""
                st.session_state["smart_obj"]  = None
                st.rerun()

    # Login status badge
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if is_logged_in:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:8px; padding:8px 12px;
             background:#f0fdf4; border:1px solid #86efac; border-radius:8px;
             font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#15803d;'>
          <span style='font-size:1rem;'>●</span>
          LOGGED IN &nbsp;·&nbsp; {login_user} &nbsp;·&nbsp; Angel One SmartAPI
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='display:flex; align-items:center; gap:8px; padding:8px 12px;
             background:#fef2f2; border:1px solid #fca5a5; border-radius:8px;
             font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#dc2626;'>
          <span style='font-size:1rem;'>●</span>
          NOT LOGGED IN
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── INSTRUMENT SETTINGS ──────────────────
    st.markdown('<div class="card"><div class="card-title">🎯 INSTRUMENT SETTINGS</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        symbol_choice = st.selectbox("Symbol", list(SYMBOL_TOKEN_MAP.keys()))
        interval      = st.selectbox("Timeframe", list(INTERVAL_MAP.keys()))
    with col2:
        from_date = st.date_input("From Date", value=datetime.today() - timedelta(days=7))
        to_date   = st.date_input("To Date",   value=datetime.today())

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚡ FETCH OHLC DATA", disabled=not is_logged_in):
        if not is_logged_in:
            st.warning("Login first using the LOGIN button above.")
        elif from_date > to_date:
            st.error("From Date must be before To Date.")
        else:
            with st.spinner(f"Fetching {symbol_choice} · {interval}..."):
                try:
                    obj = st.session_state["smart_obj"]
                    exchange, token, _ = SYMBOL_TOKEN_MAP[symbol_choice]

                    from_dt = datetime.combine(from_date, datetime.min.time().replace(hour=9, minute=15))
                    to_dt   = datetime.combine(to_date,   datetime.min.time().replace(hour=15, minute=30))

                    historic_params = {
                        "exchange":    exchange,
                        "symboltoken": token,
                        "interval":    INTERVAL_MAP[interval],
                        "fromdate":    from_dt.strftime("%Y-%m-%d %H:%M"),
                        "todate":      to_dt.strftime("%Y-%m-%d %H:%M"),
                    }

                    hist = obj.getCandleData(historic_params)

                    if not hist.get("status"):
                        st.error(f"Data fetch failed: {hist.get('message')}")
                    else:
                        raw    = hist["data"]
                        df_raw = pd.DataFrame(raw, columns=["datetime","open","high","low","close","volume"])
                        df_raw["datetime"] = pd.to_datetime(df_raw["datetime"])
                        df_raw = df_raw.sort_values("datetime").reset_index(drop=True)

                        st.session_state["fetched_df"]   = df_raw
                        st.session_state["fetch_symbol"] = symbol_choice
                        st.session_state["fetch_tf"]     = interval

                        st.success(f"✅ {len(df_raw)} candles fetched · {symbol_choice} · {interval}")

                        # Preview table — light theme
                        st.dataframe(
                            df_raw.tail(10).style.set_properties(**{
                                "background-color": "#f8fafc",
                                "color": "#0f172a",
                                "font-family": "JetBrains Mono",
                                "font-size": "12px",
                            }),
                            use_container_width=True,
                        )

                        # Download CSV
                        csv_bytes = df_raw.to_csv(index=False).encode("utf-8")
                        fname = f"{symbol_choice}_{interval.replace(' ','_')}_{from_date}_to_{to_date}.csv"
                        st.download_button(
                            label="⬇️ DOWNLOAD CSV",
                            data=csv_bytes,
                            file_name=fname,
                            mime="text/csv",
                            use_container_width=True,
                        )

                except Exception as e:
                    st.error(f"Fetch error: {str(e)}")


# ══════════════════════════════════════════════
# TAB 2 — CHART + FORECAST
# ══════════════════════════════════════════════
with tab2:

    # ── Load source ──────────────────────────
    st.markdown('<div class="card"><div class="card-title">📂 LOAD DATA</div>', unsafe_allow_html=True)

    load_source = st.radio(
        "Source",
        ["Use fetched data", "Upload CSV"],
        horizontal=True,
        label_visibility="collapsed",
    )

    df_chart = None

    if load_source == "Use fetched data":
        if "fetched_df" in st.session_state:
            df_chart = st.session_state["fetched_df"].copy()
            sym_label = st.session_state.get("fetch_symbol", "")
            tf_label  = st.session_state.get("fetch_tf", "")
            st.markdown(f'<span class="badge badge-green">✓ {sym_label} · {tf_label} · {len(df_chart)} candles</span>', unsafe_allow_html=True)
        else:
            st.info("Fetch data from Tab 1 first, or upload a CSV.")

    else:
        uploaded = st.file_uploader("Upload OHLC CSV", type=["csv"], label_visibility="collapsed")
        if uploaded:
            df_chart = pd.read_csv(uploaded)
            df_chart.columns = [c.strip().lower() for c in df_chart.columns]
            # Flexible column mapping
            col_map = {}
            for col in df_chart.columns:
                if "date" in col or "time" in col: col_map[col] = "datetime"
                elif col in ["open","o"]:           col_map[col] = "open"
                elif col in ["high","h"]:           col_map[col] = "high"
                elif col in ["low","l"]:            col_map[col] = "low"
                elif col in ["close","c","ltp"]:    col_map[col] = "close"
                elif "vol" in col:                  col_map[col] = "volume"
            df_chart.rename(columns=col_map, inplace=True)
            if "volume" not in df_chart.columns:
                df_chart["volume"] = 0
            df_chart["datetime"] = pd.to_datetime(df_chart["datetime"])
            df_chart = df_chart.sort_values("datetime").reset_index(drop=True)
            st.markdown(f'<span class="badge badge-green">✓ {len(df_chart)} candles loaded</span>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if df_chart is not None and len(df_chart) >= 20:

        # Compute BB
        df_chart = compute_bollinger_bands(df_chart)

        # ── BB Settings ──────────────────────
        with st.expander("⚙️ BB Settings", expanded=False):
            bb_period = st.slider("BB Period (SMA)", 10, 50, 20, 1)
            if bb_period != 20:
                df_chart = compute_bollinger_bands(df_chart, period=bb_period)

        # ── Metrics ──────────────────────────
        last_row  = df_chart.dropna().iloc[-1]
        prev_row  = df_chart.dropna().iloc[-2]
        pct_chg   = (last_row["close"] - prev_row["close"]) / prev_row["close"] * 100
        bb_width  = (last_row["bb_upper_25"] - last_row["bb_lower_25"]) / last_row["bb_mid"] * 100
        position  = "UPPER" if last_row["close"] > last_row["bb_mid"] else "LOWER"

        chg_class = "up" if pct_chg >= 0 else "down"
        chg_sign  = "+" if pct_chg >= 0 else ""

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box">
            <div class="metric-label">Close</div>
            <div class="metric-value">{last_row['close']:.2f}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Change</div>
            <div class="metric-value {chg_class}">{chg_sign}{pct_chg:.2f}%</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">BB Width</div>
            <div class="metric-value">{bb_width:.1f}%</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Position</div>
            <div class="metric-value">{position}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Direction + Forecast ──────────────
        st.markdown('<div class="card"><div class="card-title">🎯 MARKET DIRECTION & FORECAST</div>', unsafe_allow_html=True)

        direction = st.session_state.get("direction", None)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="dir-btn-up">', unsafe_allow_html=True)
            if st.button("▲  UP", key="btn_up"):
                st.session_state["direction"] = "UP"
                direction = "UP"
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="dir-btn-down">', unsafe_allow_html=True)
            if st.button("▼  DOWN", key="btn_down"):
                st.session_state["direction"] = "DOWN"
                direction = "DOWN"
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="dir-btn-side">', unsafe_allow_html=True)
            if st.button("↔  SIDEWAYS", key="btn_side"):
                st.session_state["direction"] = "SIDEWAYS"
                direction = "SIDEWAYS"
            st.markdown('</div>', unsafe_allow_html=True)

        n_forecast = st.slider("Forecast candles", 5, 20, 15, 1)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Build chart ──────────────────────
        forecast_df = None
        if direction:
            dir_labels = {"UP": ("forecast-up","▲ FORECASTING UP"), "DOWN": ("forecast-down","▼ FORECASTING DOWN"), "SIDEWAYS": ("forecast-side","↔ FORECASTING SIDEWAYS")}
            cls, label = dir_labels[direction]
            st.markdown(f'<div class="forecast-label {cls}">{label} · next {n_forecast} candles</div>', unsafe_allow_html=True)

            np.random.seed(42)
            forecast_df = forecast_candles(df_chart.dropna(), direction, n=n_forecast)

        fig = build_chart(df_chart.dropna(), forecast_df, direction)
        st.plotly_chart(fig, use_container_width=True, config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["select2d", "lasso2d"],
            "displaylogo": False,
        })

        # ── Forecast table ───────────────────
        if forecast_df is not None:
            with st.expander("📋 Forecast Candle Data", expanded=False):
                st.dataframe(
                    forecast_df[["datetime","open","high","low","close","bb_mid","bb_upper_20","bb_lower_20"]].round(2),
                    use_container_width=True,
                )
                csv_fc = forecast_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Forecast CSV",
                    data=csv_fc,
                    file_name="forecast_ohlc.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    elif df_chart is not None:
        st.warning("Need at least 20 candles to compute Bollinger Bands.")
    else:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #94a3b8;">
          <div style="font-size:2rem; margin-bottom:0.5rem;">📈</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:0.8rem; letter-spacing:2px; color:#94a3b8;">
            FETCH DATA FROM TAB 1<br>OR UPLOAD A CSV FILE
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — BROOKS LIVE
# ══════════════════════════════════════════════
with tab3:
    st.markdown(
        '<div class="card"><div class="card-title">🎯 BROOKS LIVE SIGNALS — NIFTY 50</div>',
        unsafe_allow_html=True,
    )

    is_logged_in = st.session_state.get("logged_in", False)

    # Controls row
    cc1, cc2, cc3, cc4 = st.columns([1.2, 1, 1, 1])
    with cc1:
        live_symbol = st.selectbox(
            "Symbol",
            list(SYMBOL_TOKEN_MAP.keys()),
            index=0,  # NIFTY 50 default
            key="live_symbol",
        )
    with cc2:
        live_tf = st.selectbox(
            "Timeframe",
            ["3 min", "5 min", "15 min"],
            index=1,  # 5 min default
            key="live_tf",
        )
    with cc3:
        lookback_days = st.selectbox(
            "Lookback",
            [1, 2, 3, 5, 7],
            index=2,
            key="live_lookback",
        )
    with cc4:
        auto_refresh = st.toggle(
            "Auto-refresh 30s",
            value=True,
            key="live_autorefresh",
        )

    min_conf = st.slider(
        "Min signal confidence",
        50, 90, 65, 5,
        key="live_min_conf",
        help="Hide signals below this confidence threshold",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-refresh
    if auto_refresh:
        # Lightweight rerun every 30s — no extra package needed
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=30 * 1000, key="brooks_autorefresh")
        except ImportError:
            # Fallback: meta refresh via session_state polling
            st.markdown(
                "<meta http-equiv='refresh' content='30'>",
                unsafe_allow_html=True,
            )

    if not is_logged_in:
        st.warning("🔑 Login from Tab 1 first — Brooks Live needs SmartAPI access.")
        st.stop()

    # ── Fetch latest candles ─────────────────────
    fetch_placeholder = st.empty()
    fetch_placeholder.info(f"⏳ Fetching {live_symbol} · {live_tf} ...")

    try:
        obj = st.session_state["smart_obj"]
        exchange, token, _ = SYMBOL_TOKEN_MAP[live_symbol]

        to_dt   = datetime.now()
        from_dt = to_dt - timedelta(days=int(lookback_days))

        params = {
            "exchange":    exchange,
            "symboltoken": token,
            "interval":    INTERVAL_MAP[live_tf],
            "fromdate":    from_dt.strftime("%Y-%m-%d %H:%M"),
            "todate":      to_dt.strftime("%Y-%m-%d %H:%M"),
        }
        hist = obj.getCandleData(params)

        if not hist.get("status"):
            fetch_placeholder.error(f"Fetch failed: {hist.get('message')}")
            st.stop()

        df_live = pd.DataFrame(
            hist["data"],
            columns=["datetime", "open", "high", "low", "close", "volume"],
        )
        df_live["datetime"] = pd.to_datetime(df_live["datetime"])
        df_live = df_live.sort_values("datetime").reset_index(drop=True)

        last_ts = df_live["datetime"].iloc[-1]
        now_ts = datetime.now()
        # Strip timezone if any for clean display
        if hasattr(last_ts, "tz_localize"):
            try:
                last_ts_display = last_ts.tz_localize(None) if last_ts.tz else last_ts
            except Exception:
                last_ts_display = last_ts
        else:
            last_ts_display = last_ts

        fetch_placeholder.markdown(
            f'<span class="badge badge-green">✓ {len(df_live)} candles · last bar: '
            f'{last_ts_display.strftime("%H:%M:%S")} · fetched at {now_ts.strftime("%H:%M:%S")}</span>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        fetch_placeholder.error(f"Fetch error: {e}")
        st.stop()

    # ── Run Brooks detection ─────────────────────
    signals = detect_brooks_signals(df_live)
    signals = [s for s in signals if s["confidence"] >= min_conf]

    # ── Metrics row ──────────────────────────────
    last_close = df_live["close"].iloc[-1]
    prev_close = df_live["close"].iloc[-2] if len(df_live) >= 2 else last_close
    pct_chg = (last_close - prev_close) / prev_close * 100
    ema20_val = _ema(df_live["close"], 20).iloc[-1]
    bias = "BULL" if last_close > ema20_val else "BEAR"
    bias_class = "up" if bias == "BULL" else "down"
    chg_class = "up" if pct_chg >= 0 else "down"
    chg_sign = "+" if pct_chg >= 0 else ""

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box">
        <div class="metric-label">Last</div>
        <div class="metric-value">{last_close:.2f}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Change</div>
        <div class="metric-value {chg_class}">{chg_sign}{pct_chg:.2f}%</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">20 EMA</div>
        <div class="metric-value">{ema20_val:.2f}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Bias</div>
        <div class="metric-value {bias_class}">{bias}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Signals</div>
        <div class="metric-value">{len(signals)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Signal alert panel ───────────────────────
    if signals:
        # Detect fresh signals (those fired on the last bar)
        last_idx = len(df_live) - 1
        fresh = [s for s in signals if s.get("bar_idx") == last_idx]

        if fresh:
            top = fresh[0]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{top['color']}22,{top['color']}11);
                 border:2px solid {top['color']}; border-radius:12px;
                 padding:14px 18px; margin:10px 0;">
              <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                <span style="font-size:1.3rem;">{top.get('signal','').split(' ')[0]}</span>
                <span style="font-family:'JetBrains Mono',monospace; font-weight:700;
                       color:{top['color']}; font-size:0.95rem;">
                  🔔 LIVE: {top['name']}
                </span>
                <span class="badge badge-amber" style="margin-left:auto;">
                  CONF {top['confidence']}%
                </span>
              </div>
              <div style="font-family:'JetBrains Mono',monospace; font-size:0.75rem;
                   color:#334155; line-height:1.7;">
                <b>Entry:</b> {top.get('entry','-')}<br>
                <b>Stop:</b> {top.get('stop','-')}<br>
                <b>Target:</b> {top.get('target','-')}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Chart ────────────────────────────────────
    fig = build_brooks_chart(df_live, signals)
    st.plotly_chart(fig, use_container_width=True, config={
        "scrollZoom": True,
        "displayModeBar": True,
        "displaylogo": False,
    })

    # ── Signal table ─────────────────────────────
    st.markdown(
        '<div class="card"><div class="card-title">📋 ALL FIRED SIGNALS</div>',
        unsafe_allow_html=True,
    )

    if signals:
        rows = []
        for s in signals:
            rows.append({
                "Signal": s["name"].replace("Brooks: ", ""),
                "Direction": s.get("direction", "-"),
                "Conf": f"{s['confidence']}%",
                "Entry": s.get("entry", "-"),
                "Stop": s.get("stop", "-"),
                "Target": s.get("target", "-"),
            })
        df_signals = pd.DataFrame(rows)
        st.dataframe(df_signals, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:2rem 1rem; color:#94a3b8;
             font-family:'JetBrains Mono',monospace; font-size:0.8rem;
             letter-spacing:2px;">
          NO BROOKS SIGNALS ABOVE THRESHOLD<br>
          <span style="font-size:0.7rem;">Market may be in chop — wait for setup</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
