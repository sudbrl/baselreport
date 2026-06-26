"""
Executive MIS Dashboard  ·  Basel Analytics  ·  v5.0
Financial Risk Intelligence Platform - Redesigned
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
import requests
import numpy as np

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Basel Analytics | Executive MIS",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DESIGN TOKENS & CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg: #0B0F19;
    --bg-gradient: radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 40%),
                   radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.05), transparent 40%);
    --card: rgba(19, 24, 38, 0.7);
    --card-solid: #131826;
    --card-hover: #1A2031;
    --border: rgba(255, 255, 255, 0.06);
    --border-hover: rgba(255, 255, 255, 0.12);
    --text: #E2E8F0;
    --text-muted: #94A3B8;
    --primary: #3B82F6;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --purple: #8B5CF6;
}

/* ─ Base ─ */
html, body, .stApp {
    background-color: var(--bg) !important;
    background-image: var(--bg-gradient) !important;
    background-attachment: fixed !important;
    color: var(--text) !important;
}
*, *::before, *::after {
    box-sizing: border-box;
    font-family: 'Inter', sans-serif !important;
}
p, li, span, label, td, th, div { color: var(--text); }

.main .block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 1600px;
}

/* ─ Sidebar ─ */
section[data-testid="stSidebar"] {
    background: rgba(11, 15, 25, 0.95) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(10px);
}
.sb-logo {
    font-size: 1.2rem; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(135deg, var(--primary), var(--success));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sb-section {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--text-muted) !important;
    margin-top: 1.5rem; margin-bottom: 0.5rem;
}

/* ─ Header ─ */
.app-header {
    display: flex; justify-content: space-between; align-items: flex-end;
    padding-bottom: 1.5rem; border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.header-title { font-size: 2rem; font-weight: 800; line-height: 1.2; margin: 0; }
.header-sub { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem; }
.header-meta { display: flex; gap: 1.5rem; }
.meta-item { text-align: right; }
.meta-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); }
.meta-val { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 600; }

/* ─ KPI Cards ─ */
.kpi-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; margin-bottom: 2rem;
}
.kpi-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    padding: 1.5rem; backdrop-filter: blur(12px);
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px;
    background: var(--primary);
}
.kpi-card.ok::before { background: var(--success); }
.kpi-card.warn::before { background: var(--warning); }
.kpi-card.danger::before { background: var(--danger); }
.kpi-card:hover {
    border-color: var(--border-hover); transform: translateY(-4px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.kpi-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); }
.kpi-badge {
    font-size: 0.6rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-badge.ok { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.kpi-badge.warn { background: rgba(245, 158, 11, 0.1); color: var(--warning); }
.kpi-badge.danger { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 2.25rem; font-weight: 700; line-height: 1; margin-bottom: 0.5rem; }
.kpi-footer { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; }
.kpi-delta { font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.kpi-delta.pos { color: var(--success); }
.kpi-delta.neg { color: var(--danger); }
.kpi-sub { color: var(--text-muted); font-size: 0.75rem; }

/* ─ Alerts ─ */
.alert-box {
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem;
    backdrop-filter: blur(12px);
}
.alert-icon { font-size: 1.5rem; }
.alert-text h4 { margin: 0; font-size: 0.9rem; font-weight: 700; }
.alert-text p { margin: 0; font-size: 0.8rem; color: var(--text-muted); }

/* ─ Section Labels ─ */
.sec-label {
    font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
    color: var(--text); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
}
.sec-label::before {
    content: ''; width: 4px; height: 16px; background: var(--primary); border-radius: 2px;
}

/* ─ Streamlit Overrides ─ */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; border-bottom: 1px solid var(--border); padding: 0; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text-muted) !important;
    padding: 0.75rem 1.25rem !important; font-size: 0.9rem !important; font-weight: 600 !important;
    border-radius: 0 !important; border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important; border-bottom: 2px solid var(--primary) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

div[data-testid="stMetric"] {
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 1rem; backdrop-filter: blur(12px);
}
div[data-testid="stMetric"] label { color: var(--text-muted) !important; font-size: 0.75rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'JetBrains Mono', monospace !important; }

.stSelectbox [data-baseweb="select"]>div,
.stMultiSelect [data-baseweb="select"]>div {
    background: var(--card-solid) !important; border-color: var(--border) !important; color: var(--text) !important;
}

.stDataFrame { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }

#MainMenu, footer, header { visibility: hidden; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        xls = pd.ExcelFile(BytesIO(r.content))
        df  = xls.parse("Data")
        
        # Clean columns
        df.columns = (df.columns.str.strip().str.replace(r'\s+', ' ', regex=True).str.replace('\xa0', ' '))
        drop = [c for c in df.columns if c.startswith("Unnamed") or c in ("Helper", "Rs.1", "Rs.2", "Movements(%)")]
        df.drop(columns=drop, errors="ignore", inplace=True)
        
        df["Month"]       = df["Month"].astype(str).str.strip()
        df["Particulars"] = df["Particulars"].astype(str).str.strip()
        df["Rs"]          = pd.to_numeric(df["Rs"], errors="coerce")
        
        # Drop rows where Month or Particulars are invalid
        df = df.dropna(subset=["Month", "Particulars"])
        df = df[df["Month"] != "nan"]
        
        return df
    except Exception:
        return None

df = load_data()
if df is None:
    st.error("⚠️ Failed to load data. Check your connection and refresh.")
    st.stop()


# ── LABEL DISCOVERY ───────────────────────────────────────────────────────────
def find_row(keywords):
    for v in df["Particulars"].dropna().unique():
        if all(k.lower() in v.lower() for k in keywords):
            return v
    return None

LBL = {
    "gross_npa":  find_row(["gross", "npa"]),
    "net_npa":    find_row(["net",   "npa"]),
    "core_cap":   find_row(["core",  "capital"]),
    "total_cap":  find_row(["total", "capital"]),
    "rwe_credit": find_row(["risk weighted exposure for credit"]),
    "rwe_op":     find_row(["risk weighted exposure for operational"]),
    "rwe_mkt":    find_row(["risk weighted exposure for market"]),
}
for name, val in LBL.items():
    if val is None:
        st.error(f"⚠️ Row label not resolved: **{name}**")
        st.stop()


# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_val(label, month):
    mask = (df["Particulars"] == label) & (df["Month"] == month)
    r    = df.loc[mask, "Rs"]
    return float(r.iloc[0]) if not r.empty and pd.notna(r.iloc[0]) else 0.0

def get_series(label, months=None):
    s = df[df["Particulars"] == label][["Month", "Rs"]].dropna(subset=["Rs"]).copy()
    if months is not None:
        s = s[s["Month"].isin(months)]
    return s.reset_index(drop=True)

def prev_month_of(month, months_list):
    idx = months_list.index(month) if month in months_list else 0
    return months_list[max(0, idx - 1)]

def is_ratio(v):   return abs(v) <= 2.0
def fmt(v):
    if pd.isna(v):  return "N/A"
    return f"{v:.2%}" if is_ratio(v) else f"{v:,.2f}"

def pct_chg(cur, prv):
    if prv is None or abs(prv) < 1e-9: return 0.0
    return ((cur - prv) / abs(prv)) * 100

def get_status(v, thr, lower_better=True):
    if lower_better:
        if v <= thr:           return "ok"
        elif v <= thr * 1.25:  return "warn"
        return "danger"
    else:
        if v >= thr:           return "ok"
        elif v >= thr * 0.8:   return "warn"
        return "danger"

def hex_to_rgba(hex, alpha):
    hex = hex.lstrip('#')
    r, g, b = int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── PLOTLY LAYOUT TEMPLATE ────────────────────────────────────────────────────
COLORS = {
    "bg": "rgba(0,0,0,0)", "text": "#E2E8F0", "muted": "#94A3B8", 
    "grid": "rgba(255,255,255,0.04)", "primary": "#3B82F6", "success": "#10B981",
    "warning": "#F59E0B", "danger": "#EF4444", "purple": "#8B5CF6"
}

PLOT_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
    font=dict(color=COLORS["text"], family="Inter", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor=COLORS["grid"], zeroline=False, tickfont=dict(color=COLORS["muted"])),
    yaxis=dict(gridcolor=COLORS["grid"], zeroline=False, tickfont=dict(color=COLORS["muted"])),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=COLORS["muted"])),
    hoverlabel=dict(bgcolor="#131826", font=dict(color=COLORS["text"]))
)

def dark_gauge(value, max_val, title, threshold, lower_better=True, color=None):
    v  = value * 100    if is_ratio(value)     else value
    t  = threshold * 100 if is_ratio(threshold) else threshold
    m  = max_val * 100  if is_ratio(max_val)   else max_val
    mx = m * 1.55

    st_cls = get_status(value, threshold, lower_better)
    bar_c  = color if color else (COLORS["success"] if st_cls == "ok" else (COLORS["warning"] if st_cls == "warn" else COLORS["danger"]))

    steps = ([{"range": [0, t], "color": hex_to_rgba(COLORS["success"], 0.15)},
              {"range": [t, t * 1.25], "color": hex_to_rgba(COLORS["warning"], 0.15)},
              {"range": [t * 1.25, mx], "color": hex_to_rgba(COLORS["danger"], 0.15)}]
             if lower_better else
             [{"range": [0, t * 0.8], "color": hex_to_rgba(COLORS["danger"], 0.15)},
              {"range": [t * 0.8, t], "color": hex_to_rgba(COLORS["warning"], 0.15)},
              {"range": [t, mx], "color": hex_to_rgba(COLORS["success"], 0.15)}])

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=v,
        gauge=dict(
            axis=dict(range=[0, mx], tickcolor=COLORS["muted"], tickfont=dict(color=COLORS["muted"], size=10)),
            bar=dict(color=bar_c, thickness=0.45),
            bgcolor=COLORS["bg"], bordercolor=COLORS["grid"], borderwidth=1,
            steps=steps,
            threshold=dict(line=dict(color=COLORS["danger"], width=3), thickness=0.8, value=t),
        ),
        number=dict(suffix="%", font=dict(size=28, color=COLORS["text"], family="JetBrains Mono")),
        title=dict(text=title, font=dict(size=12, color=COLORS["muted"], family="Inter")),
    ))
    fig.update_layout(height=220, paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"], margin=dict(l=10, r=10, t=40, b=10))
    return fig


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo">BASEL ANALYTICS</div>', unsafe_allow_html=True)
    st.caption("Executive Risk Intelligence")
    
    all_months = df["Month"].dropna().unique().tolist()
    avail_parts = df["Particulars"].dropna().unique().tolist()

    st.markdown('<div class="sb-section">Reporting Period</div>', unsafe_allow_html=True)
    selected_month = st.selectbox("Period", all_months, index=len(all_months) - 1, label_visibility="collapsed")
    pm = prev_month_of(selected_month, all_months)
    st.caption(f"Comparing against: **{pm}**")

    st.markdown('<div class="sb-section">Analysis Window</div>', unsafe_allow_html=True)
    comparison_periods = st.slider("Last N Periods", min_value=2, max_value=min(12, len(all_months)), value=6, label_visibility="collapsed")

    st.markdown('<div class="sb-section">Compliance Thresholds</div>', unsafe_allow_html=True)
    npa_threshold = st.number_input("NPA Warning (%)", value=5.0, step=0.5, format="%.1f") / 100
    cap_threshold = st.number_input("Capital Floor (%)", value=8.5, step=0.5, format="%.1f") / 100

    st.markdown('<div class="sb-section">System</div>', unsafe_allow_html=True)
    st.caption(f"🕒 {datetime.now().strftime('%Y-%m-%d  %H:%M')}")
    st.caption(f"📦 {len(df):,} records · {len(all_months)} periods")

recent_months = all_months[-comparison_periods:]

# Derived Values
kpi = dict(
    gnpa_c = get_val(LBL["gross_npa"],  selected_month),
    gnpa_p = get_val(LBL["gross_npa"],  pm),
    nnpa_c = get_val(LBL["net_npa"],    selected_month),
    nnpa_p = get_val(LBL["net_npa"],    pm),
    core_c = get_val(LBL["core_cap"],   selected_month),
    core_p = get_val(LBL["core_cap"],   pm),
    tot_c  = get_val(LBL["total_cap"],  selected_month),
    tot_p  = get_val(LBL["total_cap"],  pm),
)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
    <div>
        <h1 class="header-title">Executive MIS Dashboard</h1>
        <div class="header-sub">Basel III Compliance Monitoring & Financial Risk Intelligence</div>
    </div>
    <div class="header-meta">
        <div class="meta-item">
            <div class="meta-label">Current Period</div>
            <div class="meta-val">{selected_month}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Prior Period</div>
            <div class="meta-val">{pm}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Analysis Window</div>
            <div class="meta-val">{comparison_periods} Pds</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── KPI CARDS ─────────────────────────────────────────────────────────────────
def render_kpi_card(title, cur, prv, lower_better, thr, sub):
    delta = pct_chg(cur, prv)
    zero  = abs(delta) < 0.01
    
    if zero:
        d_cls, dtxt = "pos", "0.00%"
    else:
        up = delta > 0
        good = (up and not lower_better) or (not up and lower_better)
        d_cls = "pos" if good else "neg"
        dtxt = f"{abs(delta):.2f}%"
        
    st_cls = get_status(cur, thr, lower_better)
    
    return f"""
    <div class="kpi-card {st_cls}">
        <div class="kpi-header">
            <span class="kpi-title">{title}</span>
            <span class="kpi-badge {st_cls}">{st_cls.upper()}</span>
        </div>
        <div class="kpi-value">{fmt(cur)}</div>
        <div class="kpi-footer">
            <span class="kpi-delta {d_cls}">{'▲' if delta>=0 else '▼'} {dtxt}</span>
            <span class="kpi-sub">· {sub}</span>
        </div>
    </div>
    """

st.markdown(
    '<div class="kpi-grid">'
    + render_kpi_card("Gross NPA", kpi["gnpa_c"], kpi["gnpa_p"], True, npa_threshold, f"Limit: {fmt(npa_threshold)}")
    + render_kpi_card("Net NPA", kpi["nnpa_c"], kpi["nnpa_p"], True, npa_threshold * 0.8, f"Limit: {fmt(npa_threshold * 0.8)}")
    + render_kpi_card("Core Capital", kpi["core_c"], kpi["core_p"], False, 0.055, "Tier 1 Minimum")
    + render_kpi_card("Capital Adequacy", kpi["tot_c"], kpi["tot_p"], False, cap_threshold, "Regulatory Floor")
    + '</div>',
    unsafe_allow_html=True
)

# ── ALERTS ────────────────────────────────────────────────────────────────────
alerts = ""
if kpi["gnpa_c"] > npa_threshold:
    alerts += ('<div class="alert-box" style="border-left: 4px solid var(--danger);">'
               '<div class="alert-icon">🚨</div>'
               '<div class="alert-text"><h4>Gross NPA Breach</h4>'
               f'<p>Current {fmt(kpi["gnpa_c"])} exceeds regulatory threshold of {fmt(npa_threshold)}. Immediate escalation required.</p></div></div>')
elif kpi["tot_c"] < cap_threshold:
    alerts += ('<div class="alert-box" style="border-left: 4px solid var(--danger);">'
               '<div class="alert-icon">🚨</div>'
               '<div class="alert-text"><h4>Capital Adequacy Breach</h4>'
               f'<p>Total Capital {fmt(kpi["tot_c"])} is below the regulatory minimum of {fmt(cap_threshold)}.</p></div></div>')
else:
    alerts += ('<div class="alert-box" style="border-left: 4px solid var(--success);">'
               '<div class="alert-icon">✅</div>'
               '<div class="alert-text"><h4>All Metrics Within Regulatory Limits</h4>'
               f'<p>No compliance breaches detected as of {selected_month}. Continue monitoring period-over-period trends.</p></div></div>')

st.markdown(alerts, unsafe_allow_html=True)


# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Executive Overview",
    "📉  Asset Quality",
    "🛡️  Capital & RWA",
    "🗃️  Data Explorer",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Executive Overview
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    g1, g2, g3, g4 = st.columns(4)
    with g1: st.plotly_chart(dark_gauge(kpi["gnpa_c"], 0.15, "Gross NPA", npa_threshold, True), use_container_width=True)
    with g2: st.plotly_chart(dark_gauge(kpi["nnpa_c"], 0.10, "Net NPA", npa_threshold * 0.8, True), use_container_width=True)
    with g3: st.plotly_chart(dark_gauge(kpi["core_c"], 0.15, "Core Capital", 0.055, False), use_container_width=True)
    with g4: st.plotly_chart(dark_gauge(kpi["tot_c"], 0.20, "Total Capital", cap_threshold, False), use_container_width=True)
    
    st.markdown('<div class="sec-label">Risk & Capital Trend Analysis</div>', unsafe_allow_html=True)
    
    trend_df = df[(df["Particulars"].isin([LBL["gross_npa"], LBL["net_npa"], LBL["core_cap"], LBL["total_cap"]])) & 
                  (df["Month"].isin(recent_months))].copy()
    trend_df["Metric Type"] = trend_df["Particulars"].apply(lambda x: "NPA Ratios" if "npa" in x.lower() else "Capital Ratios")
    
    fig_trend = px.line(
        trend_df, x="Month", y="Rs", color="Particulars", markers=True,
        color_discrete_map={LBL["gross_npa"]: COLORS["danger"], LBL["net_npa"]: COLORS["warning"], 
                            LBL["core_cap"]: COLORS["primary"], LBL["total_cap"]: COLORS["success"]}
    )
    fig_trend.update_traces(mode="lines+markers", marker=dict(size=8), line=dict(width=2.5))
    fig_trend.update_layout(**PLOT_LAYOUT, height=400, yaxis=dict(gridcolor=COLORS["grid"], tickformat=".1%"))
    st.plotly_chart(fig_trend, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Asset Quality
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-label">NPA Breakdown & Movement</div>', unsafe_allow_html=True)
    
    # Get NPA Loan breakdown
    npa_cats = ["Substandard Loan", "Doubtful Loan", "Loss Loan"]
    npa_breakdown = []
    for cat in npa_cats:
        s = get_series(cat, recent_months)
        if not s.empty:
            s["Category"] = cat
            npa_breakdown.append(s)
    
    if npa_breakdown:
        npa_df = pd.concat(nppa_breakdown)
        fig_npa_bar = px.area(
            npa_df, x="Month", y="Rs", color="Category", 
            color_discrete_map={"Substandard Loan": COLORS["warning"], "Doubtful Loan": COLORS["danger"], "Loss Loan": COLORS["purple"]},
            line_group="Category"
        )
        fig_npa_bar.update_layout(**PLOT_LAYOUT, height=350)
        st.plotly_chart(fig_npa_bar, use_container_width=True)
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="sec-label">NPA Ratio Trend</div>', unsafe_allow_html=True)
        gnpa_s = get_series(LBL["gross_npa"], recent_months)
        nnpa_s = get_series(LBL["net_npa"], recent_months)
        
        fig_npa = go.Figure()
        fig_npa.add_trace(go.Scatter(x=gnpa_s["Month"], y=gnpa_s["Rs"], name="Gross NPA", fill="tozeroy", 
                                     line=dict(color=COLORS["danger"], width=2), fillcolor=hex_to_rgba(COLORS["danger"], 0.1)))
        fig_npa.add_trace(go.Scatter(x=nnpa_s["Month"], y=nnpa_s["Rs"], name="Net NPA", fill="tonexty", 
                                     line=dict(color=COLORS["warning"], width=2), fillcolor=hex_to_rgba(COLORS["warning"], 0.1)))
        fig_npa.add_hline(y=npa_threshold, line_dash="dash", line_color=COLORS["danger"], 
                          annotation_text=f"Limit {fmt(npa_threshold)}", annotation_font_color=COLORS["danger"])
        fig_npa.update_layout(**PLOT_LAYOUT, height=350, yaxis=dict(tickformat=".1%"))
        st.plotly_chart(fig_npa, use_container_width=True)
        
    with c2:
        st.markdown('<div class="sec-label">NPA Classification Reference</div>', unsafe_allow_html=True)
        ref_data = pd.DataFrame({
            "Category": ["Standard", "Sub-Standard", "Doubtful", "Loss"],
            "Definition": ["Performing; timely repayment", "NPA > 90 days", "NPA > 12 months", "Non-recoverable"],
            "Provisioning": ["0.25% – 2.00%", "15% – 25%", "25% – 100%", "100%"]
        })
        st.dataframe(ref_data, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Capital & RWA
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-label">Risk Weighted Exposures (Current Period)</div>', unsafe_allow_html=True)
    
    rwe_data = {
        "Credit Risk": get_val(LBL["rwe_credit"], selected_month),
        "Operational Risk": get_val(LBL["rwe_op"], selected_month),
        "Market Risk": get_val(LBL["rwe_mkt"], selected_month)
    }
    
    rwe_df = pd.DataFrame(list(rwe_data.items()), columns=["Risk Type", "Exposure"])
    fig_rwe = px.bar(rwe_df, x="Risk Type", y="Exposure", text="Exposure",
                     color="Risk Type", color_discrete_sequence=[COLORS["primary"], COLORS["purple"], COLORS["warning"]])
    fig_rwe.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_color=COLORS["muted"])
    fig_rwe.update_layout(**PLOT_LAYOUT, height=350, showlegend=False)
    st.plotly_chart(fig_rwe, use_container_width=True)
    
    st.markdown('<div class="sec-label">Capital Buffer Over Time</div>', unsafe_allow_html=True)
    core_s  = get_series(LBL["core_cap"], recent_months)
    total_s = get_series(LBL["total_cap"], recent_months)
    
    fig_cap = go.Figure()
    fig_cap.add_trace(go.Scatter(x=total_s["Month"], y=total_s["Rs"], name="Total Capital", fill="tozeroy", 
                                 line=dict(color=COLORS["success"], width=2.5), fillcolor=hex_to_rgba(COLORS["success"], 0.15)))
    fig_cap.add_trace(go.Scatter(x=core_s["Month"], y=core_s["Rs"], name="Core Capital", fill="tonexty", 
                                 line=dict(color=COLORS["primary"], width=2.5), fillcolor=hex_to_rgba(COLORS["primary"], 0.15)))
    fig_cap.add_hline(y=cap_threshold, line_dash="dash", line_color=COLORS["danger"], 
                      annotation_text=f"Min {fmt(cap_threshold)}", annotation_font_color=COLORS["danger"])
    fig_cap.update_layout(**PLOT_LAYOUT, height=400, yaxis=dict(tickformat=".1%"))
    st.plotly_chart(fig_cap, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Data Explorer
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-label">Interactive Dataset</div>', unsafe_allow_html=True)
    
    cf1, cf2 = st.columns(2)
    with cf1:
        part_filter = st.multiselect("Filter by Metric", avail_parts, key="explorer_filter")
    with cf2:
        sort_col = st.selectbox("Sort By", ["Month", "Particulars", "Rs"], key="explorer_sort")
        
    explorer_df = df.copy()
    explorer_df = explorer_df[explorer_df["Month"].isin(recent_months)]
    if part_filter:
        explorer_df = explorer_df[explorer_df["Particulars"].isin(part_filter)]
    explorer_df = explorer_df.sort_values([sort_col, "Month"])
    
    c1, c2 = st.columns([4, 1])
    with c1:
        st.caption(f"Displaying **{len(explorer_df)}** records from the last **{comparison_periods}** periods.")
    with c2:
        st.download_button("📥 Export CSV", explorer_df.to_csv(index=False), "basel_export.csv", "text/csv")
        
    st.dataframe(
        explorer_df, use_container_width=True, hide_index=True,
        column_config={
            "Rs": st.column_config.NumberColumn(format="%.2f"),
            "Month": st.column_config.TextColumn(width="small"),
            "Particulars": st.column_config.TextColumn(width="large"),
        }
    )
