"""
Executive MIS Dashboard — Redesigned
Basel Analytics | Financial Risk Intelligence Platform
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

# ─────────────────────── Page Configuration ───────────────────────
st.set_page_config(
    page_title="Executive MIS | Basel Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────── Design Tokens ───────────────────────
PALETTE = {
    "bg":             "#F1F5F9",
    "card":           "#FFFFFF",
    "navy":           "#0F172A",
    "navy_mid":       "#1E293B",
    "navy_light":     "#334155",
    "blue":           "#2563EB",
    "blue_soft":      "#3B82F6",
    "blue_pale":      "#DBEAFE",
    "emerald":        "#059669",
    "emerald_pale":   "#D1FAE5",
    "amber":          "#D97706",
    "amber_pale":     "#FEF3C7",
    "red":            "#DC2626",
    "red_pale":       "#FEE2E2",
    "slate":          "#64748B",
    "slate_light":    "#94A3B8",
    "border":         "#E2E8F0",
    "border_soft":    "#F1F5F9",
    "gradient_start": "#0F172A",
    "gradient_end":   "#1E3A8A",
}

# ─────────────────────── Custom CSS ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg:#F1F5F9; --card:#FFF; --navy:#0F172A; --navy-mid:#1E293B;
    --blue:#2563EB; --blue-soft:#3B82F6; --blue-pale:#DBEAFE;
    --emerald:#059669; --emerald-pale:#D1FAE5;
    --amber:#D97706; --amber-pale:#FEF3C7;
    --red:#DC2626; --red-pale:#FEE2E2;
    --slate:#64748B; --slate-light:#94A3B8; --border:#E2E8F0;
}

*{font-family:'DM Sans',system-ui,sans-serif;box-sizing:border-box}
.main{background:var(--bg)}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0F172A 0%,#1E293B 60%,#0F172A 100%)!important;
    border-right:1px solid rgba(255,255,255,0.06)!important;
}
section[data-testid="stSidebar"] *{color:#CBD5E1!important}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stCheckbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stNumberInput label{color:#94A3B8!important;font-size:.78rem;font-weight:600;letter-spacing:.3px;text-transform:uppercase}
section[data-testid="stSidebar"] .stSelectbox>div>div,
section[data-testid="stSidebar"] .stNumberInput>div>div{
    background:rgba(255,255,255,0.06)!important;border-color:rgba(255,255,255,0.1)!important;
    border-radius:10px!important;color:#F1F5F9!important;
}
section[data-testid="stSidebar"] .stSlider>div>div>div>div{background:var(--blue)!important}

.sidebar-brand{text-align:center;padding:1.6rem 0 1rem;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:1rem}
.sidebar-brand h2{margin:0;font-size:1.25rem;font-weight:800;color:#F1F5F9!important;letter-spacing:-.3px}
.sidebar-brand p{margin:.35rem 0 0;font-size:.72rem;color:#64748B!important;letter-spacing:1.5px;text-transform:uppercase;font-weight:600}
.sidebar-divider{height:1px;background:rgba(255,255,255,0.07);margin:1.1rem 0}
.sidebar-section-label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#475569!important;margin-bottom:.65rem}
.sidebar-stat{display:flex;justify-content:space-between;padding:.45rem 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:.8rem}
.sidebar-stat span:first-child{color:#64748B!important}
.sidebar-stat span:last-child{color:#CBD5E1!important;font-weight:600;font-family:'JetBrains Mono',monospace;font-size:.78rem}

/* ── Header ── */
.dash-header{
    background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 50%,#1D4ED8 100%);
    padding:2rem 2.2rem;border-radius:18px;margin-bottom:1.5rem;color:#fff;
    position:relative;overflow:hidden;
}
.dash-header::before{
    content:'';position:absolute;top:-40%;right:-10%;width:400px;height:400px;
    background:radial-gradient(circle,rgba(59,130,246,0.18) 0%,transparent 70%);
    border-radius:50%;pointer-events:none;
}
.dash-header::after{
    content:'';position:absolute;bottom:-50%;left:20%;width:300px;height:300px;
    background:radial-gradient(circle,rgba(16,185,129,0.1) 0%,transparent 70%);
    border-radius:50%;pointer-events:none;
}
.dash-header h1{font-size:1.75rem;font-weight:800;margin:0;letter-spacing:-.5px;position:relative}
.dash-header .subtitle{opacity:.7;font-size:.88rem;margin-top:.4rem;font-weight:400;position:relative}
.header-meta{display:flex;gap:1.8rem;margin-top:1rem;font-size:.82rem;position:relative;flex-wrap:wrap}
.header-meta span{opacity:.85;display:flex;align-items:center;gap:.35rem}
.header-meta strong{color:#fff;font-weight:700}

/* ── Executive Summary Bar ── */
.exec-summary{
    display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem;
}
@media(max-width:900px){.exec-summary{grid-template-columns:repeat(2,1fr)}}

.kpi-card{
    background:var(--card);border-radius:14px;padding:1.35rem 1.4rem;
    border:1px solid var(--border);position:relative;overflow:hidden;
    transition:transform .22s cubic-bezier(.4,0,.2,1),box-shadow .22s cubic-bezier(.4,0,.2,1);
    cursor:default;
}
.kpi-card:hover{transform:translateY(-3px);box-shadow:0 12px 24px -8px rgba(15,23,42,.12)}
.kpi-card::before{
    content:'';position:absolute;top:0;left:0;width:4px;height:100%;border-radius:4px 0 0 4px;
}
.kpi-card.blue::before{background:var(--blue)}
.kpi-card.emerald::before{background:var(--emerald)}
.kpi-card.amber::before{background:var(--amber)}
.kpi-card.red::before{background:var(--red)}

.kpi-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.6rem}
.kpi-label{font-size:.7rem;color:var(--slate);font-weight:700;text-transform:uppercase;letter-spacing:.8px;line-height:1.3}
.kpi-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem}
.kpi-icon.blue{background:var(--blue-pale);color:var(--blue)}
.kpi-icon.emerald{background:var(--emerald-pale);color:var(--emerald)}
.kpi-icon.amber{background:var(--amber-pale);color:var(--amber)}
.kpi-icon.red{background:var(--red-pale);color:var(--red)}

.kpi-value{font-size:1.65rem;font-weight:800;color:var(--navy);line-height:1.1;margin-bottom:.5rem;font-family:'JetBrains Mono','DM Sans',monospace}
.kpi-footer{display:flex;justify-content:space-between;align-items:center}
.kpi-delta{font-size:.78rem;font-weight:600;display:flex;align-items:center;gap:.2rem}
.kpi-delta.up{color:var(--emerald)}
.kpi-delta.down{color:var(--red)}
.kpi-delta.flat{color:var(--slate)}
.kpi-delta .arrow{font-size:.7rem}

.status-pill{
    font-size:.65rem;font-weight:700;padding:.18rem .6rem;border-radius:999px;
    text-transform:uppercase;letter-spacing:.5px;
}
.status-pill.safe{background:var(--emerald-pale);color:#065F46}
.status-pill.warn{background:var(--amber-pale);color:#92400E}
.status-pill.breach{background:var(--red-pale);color:#991B1B}

/* ── Alert Banner ── */
.alert-banner{
    padding:.85rem 1.2rem;border-radius:12px;margin-bottom:1.25rem;
    display:flex;align-items:center;gap:.75rem;font-size:.88rem;
    animation:slideIn .35s ease-out;
}
@keyframes slideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.alert-banner.critical{background:#FEF2F2;border:1px solid #FECACA;color:#991B1B}
.alert-banner.critical .alert-icon{color:var(--red)}
.alert-banner.caution{background:#FFFBEB;border:1px solid #FDE68A;color:#92400E}
.alert-banner.caution .alert-icon{color:var(--amber)}
.alert-banner.ok{background:#F0FDF4;border:1px solid #BBF7D0;color:#166534}
.alert-banner.ok .alert-icon{color:var(--emerald)}
.alert-banner strong{font-weight:700}
.alert-icon{font-size:1.25rem;flex-shrink:0}

/* ── Section Header ── */
.sec-head{
    font-size:1.05rem;font-weight:700;color:var(--navy);
    margin-bottom:.85rem;padding-bottom:.55rem;
    border-bottom:2px solid var(--blue);display:flex;align-items:center;gap:.5rem;
}
.sec-head .sec-icon{font-size:1.1rem}

/* ── Data Table Styling ── */
.data-table-wrap{border:1px solid var(--border);border-radius:12px;overflow:hidden}
.data-table-wrap th{background:#F8FAFC!important;font-weight:700!important;font-size:.78rem!important;text-transform:uppercase;letter-spacing:.5px;color:var(--slate)!important}
.data-table-wrap td{font-size:.84rem!important}
.data-table-wrap tr:hover td{background:#F8FAFC!important}

/* ── Tab Styling ── */
.stTabs [data-baseweb="tab-list"]{gap:.25rem;background:transparent;padding:0}
.stTabs [data-baseweb="tab"]{
    border-radius:10px 10px 0 0!important;padding:.6rem 1.2rem!important;
    font-weight:600!important;font-size:.84rem!important;color:var(--slate)!important;
    background:transparent!important;transition:all .2s;
}
.stTabs [aria-selected="true"]{
    background:var(--card)!important;color:var(--navy)!important;
    box-shadow:0 -2px 0 var(--blue) inset;
}
.stTabs [data-baseweb="tab-highlight"]{background-color:var(--blue)!important;height:3px!important;border-radius:3px!important}
.stTabs [data-baseweb="tab-border"]{display:none}

/* ── Misc ── */
.pill-row{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem}
.pill{
    font-size:.72rem;font-weight:600;padding:.3rem .8rem;border-radius:999px;
    border:1px solid var(--border);color:var(--slate);cursor:pointer;
    transition:all .2s;background:var(--card);
}
.pill.active{background:var(--navy);color:#fff;border-color:var(--navy)}
.pill:hover:not(.active){border-color:var(--blue);color:var(--blue)}

.scorecard-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.85rem}
.scorecard-item{
    background:var(--card);border:1px solid var(--border);border-radius:12px;
    padding:1rem 1.1rem;transition:transform .2s,box-shadow .2s;
}
.scorecard-item:hover{transform:translateY(-2px);box-shadow:0 8px 16px -6px rgba(0,0,0,.08)}
.scorecard-metric{font-size:.72rem;font-weight:600;color:var(--slate);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.4rem}
.scorecard-val{font-size:1.15rem;font-weight:800;color:var(--navy);font-family:'JetBrains Mono',monospace}
.scorecard-bar{height:6px;border-radius:3px;background:#E2E8F0;margin-top:.6rem;overflow:hidden}
.scorecard-bar-fill{height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1)}

#MainMenu{visibility:hidden}
footer{visibility:hidden}

/* Plotly chart container rounded */
.js-plotly-plot .plotly{border-radius:12px!important}
</style>
""", unsafe_allow_html=True)

# ─────────────────────── Data Loading ───────────────────────
@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        xls = pd.ExcelFile(BytesIO(resp.content))
        df = xls.parse("Data")
        df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True).str.replace('\xa0', ' ')
        drop = [c for c in df.columns if c.startswith("Unnamed") or c in ("Helper", "Rs.1", "Rs.2", "Movements(%)")]
        df.drop(columns=drop, errors="ignore", inplace=True)
        df["Month"] = df["Month"].astype(str).str.strip()
        df["Particulars"] = df["Particulars"].astype(str).str.strip()
        df["Rs"] = pd.to_numeric(df["Rs"], errors="coerce")
        return df
    except Exception:
        return None

df = load_data()

if df is None:
    st.error("⚠️  Failed to load data. Please check your connection and try again.")
    st.stop()

# ─────────────────────── Lookup Utility ───────────────────────
def find_particular(df_: pd.DataFrame, keywords: list) -> str | None:
    for val in df_["Particulars"].dropna().unique():
        vl = str(val).lower()
        if all(kw.lower() in vl for kw in keywords):
            return val
    return None

LABEL_GROSS_NPA = find_particular(df, ["gross", "npa"])
LABEL_NET_NPA   = find_particular(df, ["net", "npa"])
LABEL_CORE_CAP  = find_particular(df, ["core", "capital"])
LABEL_TOTAL_CAP = find_particular(df, ["total", "capital"])

missing = [k for k, v in {"Gross NPA": LABEL_GROSS_NPA, "Net NPA": LABEL_NET_NPA,
                            "Core Capital": LABEL_CORE_CAP, "Total Capital": LABEL_TOTAL_CAP}.items() if v is None]
if missing:
    st.error(f"⚠️  Could not find row labels for: **{', '.join(missing)}**")
    st.stop()

# ─────────────────────── Helpers ───────────────────────
def get_value(label: str, month: str) -> float:
    r = df.loc[(df["Particulars"] == label) & (df["Month"] == month), "Rs"]
    return float(r.iloc[0]) if not r.empty and pd.notna(r.iloc[0]) else 0.0

def get_series(label: str) -> pd.DataFrame:
    s = df[df["Particulars"] == label][["Month", "Rs"]].dropna(subset=["Rs"]).reset_index(drop=True)
    return s

def prev_month(month: str) -> str:
    ms = df["Month"].dropna().unique().tolist()
    i = ms.index(month) if month in ms else 0
    return ms[max(0, i - 1)]

def is_ratio(v: float) -> bool:
    return abs(v) <= 2.0

def fmt(v: float) -> str:
    if pd.isna(v): return "N/A"
    return f"{v:.2%}" if is_ratio(v) else f"{v:,.2f}"

def pct_change(cur: float, prv: float) -> float | None:
    if abs(prv) < 1e-9: return None
    return ((cur - prv) / abs(prv)) * 100

def status_class(val: float, thresh: float, lower_better: bool = True) -> str:
    if lower_better:
        return "safe" if val <= thresh else ("warn" if val <= thresh * 1.2 else "breach")
    return "safe" if val >= thresh else ("warn" if val >= thresh * 0.8 else "breach")

def sparkline_html(series: pd.Series, color: str = "#2563EB", w: int = 80, h: int = 28) -> str:
    """Generate an inline SVG sparkline from a numeric series."""
    vals = series.dropna().values
    if len(vals) < 2:
        return ""
    mn, mx = vals.min(), vals.max()
    rng = mx - mn if mx != mn else 1
    pts = []
    for i, v in enumerate(vals):
        x = (i / (len(vals) - 1)) * w
        y = h - ((v - mn) / rng) * (h - 4) - 2
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block"><polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def gauge_chart(value: float, max_val: float, title: str, threshold: float,
                lower_better: bool = True, height: int = 220) -> go.Figure:
    v = value * 100 if is_ratio(value) else value
    t = threshold * 100 if is_ratio(threshold) else threshold
    m = max_val * 100 if is_ratio(max_val) else max_val

    if lower_better:
        steps = [{"range": [0, t * 0.6], "color": "#D1FAE5"},
                 {"range": [t * 0.6, t], "color": "#FEF3C7"},
                 {"range": [t, m * 1.5], "color": "#FEE2E2"}]
        bar_col = "#059669" if v <= t else ("#D97706" if v <= t * 1.2 else "#DC2626")
    else:
        steps = [{"range": [0, t * 0.8], "color": "#FEE2E2"},
                 {"range": [t * 0.8, t], "color": "#FEF3C7"},
                 {"range": [t, m * 1.5], "color": "#D1FAE5"}]
        bar_col = "#059669" if v >= t else ("#D97706" if v >= t * 0.8 else "#DC2626")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=v,
        gauge={"axis": {"range": [0, m * 1.5], "tickfont": {"size": 10, "color": "#64748B"}},
               "bar": {"color": bar_col, "thickness": 0.55},
               "steps": steps,
               "threshold": {"line": {"color": "#94A3B8", "width": 2, "dash": "dot"}, "value": t}},
        number={"font": {"size": 28, "family": "JetBrains Mono", "color": "#0F172A"}, "suffix": "%"},
        title={"text": title, "font": {"size": 13, "color": "#64748B", "weight": 600}}
    ))
    fig.update_layout(height=height, margin=dict(l=18, r=18, t=55, b=12),
                      paper_bgcolor="rgba(0,0,0,0)")
    return fig

# ─────────────────────── Sidebar ───────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>◆ Basel Analytics</h2>
        <p>MIS Dashboard v4.0</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Reporting Period</div>', unsafe_allow_html=True)
    all_months = df["Month"].dropna().unique().tolist()
    sel_month = st.selectbox("Period", options=all_months, index=len(all_months) - 1, label_visibility="collapsed")
    p_month = prev_month(sel_month)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Metric Selection</div>', unsafe_allow_html=True)
    avail = df["Particulars"].dropna().unique().tolist()
    sel_parts = st.multiselect("Metrics", options=avail,
                               default=avail[:4] if len(avail) >= 4 else avail,
                               label_visibility="collapsed")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Analysis</div>', unsafe_allow_html=True)
    show_tbl = st.checkbox("Data Tables", value=True)
    show_raw = st.checkbox("Raw Data", value=False)
    comp_n = st.slider("Compare Periods", 1, 6, 3)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Thresholds</div>', unsafe_allow_html=True)
    npa_thr = st.number_input("NPA Warning (%)", value=5.0, step=0.5, format="%.1f") / 100
    cap_thr = st.number_input("Capital Floor (%)", value=8.5, step=0.5, format="%.1f") / 100

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">System</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-stat"><span>Updated</span><span>{datetime.now().strftime('%d %b %H:%M')}</span></div>
    <div class="sidebar-stat"><span>Records</span><span>{len(df):,}</span></div>
    <div class="sidebar-stat"><span>Periods</span><span>{len(all_months)}</span></div>
    <div class="sidebar-stat"><span>Metrics</span><span>{len(avail)}</span></div>
    """, unsafe_allow_html=True)

# ─────────────────────── KPI Data ───────────────────────
K = {
    "gnpa_c": get_value(LABEL_GROSS_NPA, sel_month), "gnpa_p": get_value(LABEL_GROSS_NPA, p_month),
    "nnpa_c": get_value(LABEL_NET_NPA, sel_month),   "nnpa_p": get_value(LABEL_NET_NPA, p_month),
    "ccap_c": get_value(LABEL_CORE_CAP, sel_month),   "ccap_p": get_value(LABEL_CORE_CAP, p_month),
    "tcap_c": get_value(LABEL_TOTAL_CAP, sel_month),  "tcap_p": get_value(LABEL_TOTAL_CAP, p_month),
}

# ─────────────────────── Header ───────────────────────
st.markdown(f"""
<div class="dash-header">
    <h1>Executive MIS Dashboard</h1>
    <p class="subtitle">Financial Risk Intelligence · Basel III Compliance Monitoring</p>
    <div class="header-meta">
        <span>📅 <strong>{sel_month}</strong> (current)</span>
        <span>📆 <strong>{p_month}</strong> (prior)</span>
        <span>📊 <strong>{len(df):,}</strong> data points</span>
        <span>🏛️ <strong>{len(avail)}</strong> metrics tracked</span>
    </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────── Alert Banners ───────────────────────
alerts = []
if K["gnpa_c"] > npa_thr:
    alerts.append(("critical", "🚨", f"<strong>Gross NPA Breach:</strong> {K['gnpa_c']:.2%} exceeds {npa_thr:.1%} threshold"))
elif K["gnpa_c"] > npa_thr * 0.8:
    alerts.append(("caution", "⚠️", f"<strong>NPA Watch:</strong> Gross NPA at {K['gnpa_c']:.2%}, approaching {npa_thr:.1%} limit"))
if K["tcap_c"] < cap_thr:
    alerts.append(("critical", "🚨", f"<strong>Capital Breach:</strong> Total Capital at {K['tcap_c']:.2%}, below {cap_thr:.1%} floor"))
elif K["tcap_c"] < cap_thr * 1.2:
    alerts.append(("caution", "⚠️", f"<strong>Capital Buffer Thin:</strong> {K['tcap_c']:.2%} adequacy, near {cap_thr:.1%} minimum"))
if not alerts:
    alerts.append(("ok", "✅", "<strong>All Clear:</strong> No regulatory breaches detected for the current period"))

for cls, icon, msg in alerts:
    st.markdown(f'<div class="alert-banner {cls}"><span class="alert-icon">{icon}</span><span>{msg}</span></div>', unsafe_allow_html=True)

# ─────────────────────── KPI Cards ───────────────────────
def kpi_card(label: str, cur: float, prv: float, series: pd.Series,
             lower_better: bool, threshold: float, color: str, icon: str):
    delta = cur - prv
    improving = (delta < 0 and lower_better) or (delta > 0 and not lower_better)
    zero = abs(delta) < 1e-9
    if zero:
        dc, arrow, dtxt = "flat", "→", "No change"
    else:
        dc = "up" if improving else "down"
        arrow = "↑" if delta > 0 else "↓"
        pc = pct_change(cur, prv)
        dtxt = f"{abs(pc):,.1f}%" if pc is not None and abs(pc) < 1e6 else f"{fmt(abs(delta))}"

    sc = status_class(cur, threshold, lower_better)
    sl = {"safe": "Compliant", "warn": "Watch", "breach": "Breach"}[sc]
    spark = sparkline_html(series, color)

    return f"""
    <div class="kpi-card {color}">
        <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon {color}">{icon}</div>
        </div>
        <div class="kpi-value">{fmt(cur)}</div>
        <div class="kpi-footer">
            <div class="kpi-delta {dc}"><span class="arrow">{arrow}</span> {dtxt} vs prior</div>
            <span class="status-pill {sc}">{sl}</span>
        </div>
        <div style="margin-top:.65rem;opacity:.7">{spark}</div>
    </div>"""

gnpa_s = get_series(LABEL_GROSS_NPA)["Rs"]
nnpa_s = get_series(LABEL_NET_NPA)["Rs"]
ccap_s = get_series(LABEL_CORE_CAP)["Rs"]
tcap_s = get_series(LABEL_TOTAL_CAP)["Rs"]

cards = [
    kpi_card("Gross NPA", K["gnpa_c"], K["gnpa_p"], gnpa_s, True, npa_thr, "red", "📉"),
    kpi_card("Net NPA",   K["nnpa_c"], K["nnpa_p"], nnpa_s, True, npa_thr * 0.8, "amber", "📊"),
    kpi_card("Core Capital (Tier I)", K["ccap_c"], K["ccap_p"], ccap_s, False, 0.055, "blue", "🏦"),
    kpi_card("Capital Adequacy", K["tcap_c"], K["tcap_p"], tcap_s, False, cap_thr, "emerald", "🛡️"),
]
st.markdown(f'<div class="exec-summary">{"".join(cards)}</div>', unsafe_allow_html=True)

# ─────────────────────── Tabs ───────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Performance", "📉 Asset Quality", "🛡️ Capital", "🗺️ Risk Scorecard", "📋 Data Explorer"
])

# ── Tab 1: Performance ─────────────────────────────────────
with tab1:
    st.markdown('<div class="sec-head"><span class="sec-icon">📈</span> Multi-Metric Trend</div>', unsafe_allow_html=True)
    if not sel_parts:
        st.warning("Select metrics from the sidebar.")
    else:
        tdf = df[df["Particulars"].isin(sel_parts)].copy()
        fig1 = px.line(tdf, x="Month", y="Rs", color="Particulars", markers=True,
                       template="plotly_white", color_discrete_sequence=px.colors.qualitative.Set2)
        fig1.update_traces(mode="lines+markers", marker=dict(size=9, line=dict(width=2, color="#fff")),
                           line=dict(width=2.5))
        fig1.update_layout(hovermode="x unified",
                           legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                                       font=dict(size=11, color="#64748B")),
                           xaxis_title="", yaxis_title="Value",
                           height=420, margin=dict(b=90),
                           plot_bgcolor="#FAFBFC", paper_bgcolor="#FAFBFC",
                           xaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0"),
                           yaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0"))
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown('<div class="sec-head"><span class="sec-icon">📊</span> NPA Side-by-Side</div>', unsafe_allow_html=True)
    gs, ns = get_series(LABEL_GROSS_NPA), get_series(LABEL_NET_NPA)
    fc = make_subplots(rows=1, cols=2, subplot_titles=("Gross NPA", "Net NPA"), horizontal_spacing=0.12)
    fc.add_trace(go.Bar(x=gs["Month"], y=gs["Rs"], marker_color="#1E3A8A",
                        texttemplate="%{y:.2%}" if is_ratio(gs["Rs"].iloc[0]) else "%{y:,.2f}",
                        textposition="outside", textfont=dict(size=10, color="#1E3A8A")),
                 row=1, col=1)
    fc.add_trace(go.Bar(x=ns["Month"], y=ns["Rs"], marker_color="#059669",
                        texttemplate="%{y:.2%}" if is_ratio(ns["Rs"].iloc[0]) else "%{y:,.2f}",
                        textposition="outside", textfont=dict(size=10, color="#059669")),
                 row=1, col=2)
    fc.add_hline(y=npa_thr, line_dash="dash", line_color="#DC2626", line_width=1.5,
                 annotation_text=f"Limit {npa_thr:.1%}", annotation_font_size=10, row=1, col=1)
    fc.add_hline(y=npa_thr * 0.8, line_dash="dash", line_color="#DC2626", line_width=1.5,
                 annotation_text=f"Limit {npa_thr*0.8:.1%}", annotation_font_size=10, row=1, col=2)
    fc.update_layout(height=340, showlegend=False, template="plotly_white",
                     plot_bgcolor="#FAFBFC", paper_bgcolor="#FAFBFC",
                     xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"))
    st.plotly_chart(fc, use_container_width=True)

    if show_tbl:
        st.markdown('<div class="sec-head"><span class="sec-icon">📋</span> Summary Table</div>', unsafe_allow_html=True)
        rows = []
        for label, db in [("Gross NPA", LABEL_GROSS_NPA), ("Net NPA", LABEL_NET_NPA),
                           ("Core Capital", LABEL_CORE_CAP), ("Total Capital", LABEL_TOTAL_CAP)]:
            s = get_series(db)
            if len(s) >= 2:
                c_, p_ = s["Rs"].iloc[-1], s["Rs"].iloc[-2]
                pc = pct_change(c_, p_)
                ch = f"{pc:+.2f}%" if pc is not None else "N/A"
            elif len(s) == 1:
                c_, ch = s["Rs"].iloc[-1], "N/A"
            else:
                continue
            rows.append({"Metric": label, "Current": fmt(c_), "Min": fmt(s["Rs"].min()),
                         "Max": fmt(s["Rs"].max()), "Avg": fmt(s["Rs"].mean()), "Δ vs Prior": ch})
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                         column_config={"Δ vs Prior": st.column_config.TextColumn("Δ vs Prior")})

# ── Tab 2: Asset Quality ────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-head"><span class="sec-icon">📉</span> NPA Gauges</div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(gauge_chart(K["gnpa_c"], 0.15, "Gross NPA Ratio", npa_thr, True), use_container_width=True)
    with g2:
        st.plotly_chart(gauge_chart(K["nnpa_c"], 0.10, "Net NPA Ratio", npa_thr * 0.8, True), use_container_width=True)

    st.markdown('<div class="sec-head"><span class="sec-icon">📊</span> NPA Composition Trend</div>', unsafe_allow_html=True)
    fig_npa = go.Figure()
    fig_npa.add_trace(go.Bar(x=gs["Month"], y=gs["Rs"], name="Gross NPA",
                             marker_color="rgba(30,58,138,0.75)", texttemplate="%{y:.2%}" if is_ratio(gs["Rs"].iloc[0]) else "%{y}",
                             textposition="inside", textfont=dict(size=10, color="#fff")))
    fig_npa.add_trace(go.Bar(x=ns["Month"], y=ns["Rs"], name="Net NPA",
                             marker_color="rgba(5,150,105,0.85)", texttemplate="%{y:.2%}" if is_ratio(ns["Rs"].iloc[0]) else "%{y}",
                             textposition="inside", textfont=dict(size=10, color="#fff")))
    # Provisioning coverage (implicit)
    prov = gs["Rs"].values - ns["Rs"].values
    fig_npa.add_trace(go.Scatter(x=gs["Month"], y=prov, name="Provisioning Coverage",
                                 mode="lines+markers", line=dict(color="#D97706", width=2.5, dash="dot"),
                                 marker=dict(size=8, color="#D97706")))
    fig_npa.update_layout(barmode="group", template="plotly_white", height=400,
                          hovermode="x unified",
                          legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(size=11)),
                          xaxis_title="", yaxis_title="Ratio",
                          plot_bgcolor="#FAFBFC", paper_bgcolor="#FAFBFC",
                          xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"))
    st.plotly_chart(fig_npa, use_container_width=True)

    with st.expander("📚 NPA Classification Standards (Basel III)"):
        st.markdown("""
| Category | Definition | Provisioning |
|----------|------------|-------------|
| **Standard** | Performing, timely repayment | 0.25% – 2.00% |
| **Sub-Standard** | NPA > 90 days | 15% – 25% |
| **Doubtful** | NPA > 12 months | 25% – 100% |
| **Loss Asset** | Non-recoverable | 100% |
""")

    if show_tbl:
        nc = gs.merge(ns, on="Month", suffixes=("_Gross", "_Net"))
        nc.columns = ["Month", "Gross NPA", "Net NPA"]
        nc["Provisioning"] = nc["Gross NPA"] - nc["Net NPA"]
        nc["Coverage %"] = (nc["Provisioning"] / nc["Gross NPA"].replace(0, np.nan) * 100).round(1)
        st.markdown("### NPA Detail")
        st.dataframe(nc, use_container_width=True, hide_index=True)

# ── Tab 3: Capital ──────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-head"><span class="sec-icon">🛡️</span> Capital Position Gauges</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(gauge_chart(K["ccap_c"], 0.15, "Core Capital", 0.055, False), use_container_width=True)
    with g2:
        st.plotly_chart(gauge_chart(K["tcap_c"], 0.20, "Total Capital", cap_thr, False), use_container_width=True)
    with g3:
        buf = max(K["tcap_c"] - cap_thr, 0)
        st.plotly_chart(gauge_chart(buf, cap_thr * 0.5, "Capital Buffer", cap_thr * 0.1, False), use_container_width=True)

    st.markdown('<div class="sec-head"><span class="sec-icon">📊</span> Capital Stack Over Time</div>', unsafe_allow_html=True)
    cs = get_series(LABEL_CORE_CAP)
    ts = get_series(LABEL_TOTAL_CAP)
    cd = cs.merge(ts, on="Month", suffixes=("_Core", "_Total"))
    cd.columns = ["Month", "Core", "Total"]
    cd["Tier II"] = cd["Total"] - cd["Core"]

    fig_cap = go.Figure()
    fig_cap.add_trace(go.Scatter(x=cd["Month"], y=cd["Core"], name="Core (Tier I)",
                                 fill="tozeroy", mode="lines+markers",
                                 line=dict(color="#2563EB", width=2.5),
                                 fillcolor="rgba(37,99,235,0.15)",
                                 marker=dict(size=7, color="#2563EB")))
    fig_cap.add_trace(go.Scatter(x=cd["Month"], y=cd["Total"], name="Total Capital",
                                 fill="tonexty", mode="lines+markers",
                                 line=dict(color="#0F172A", width=2.5),
                                 fillcolor="rgba(15,23,42,0.12)",
                                 marker=dict(size=7, color="#0F172A")))
    fig_cap.add_hline(y=cap_thr, line_dash="dash", line_color="#DC2626", line_width=2,
                      annotation_text=f"Regulatory Min ({cap_thr:.1%})",
                      annotation_position="bottom right", annotation_font=dict(size=10, color="#DC2626"))
    fig_cap.update_layout(template="plotly_white", height=400, hovermode="x unified",
                          legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center", font=dict(size=11)),
                          xaxis_title="", yaxis_title="Ratio",
                          plot_bgcolor="#FAFBFC", paper_bgcolor="#FAFBFC",
                          xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"))
    st.plotly_chart(fig_cap, use_container_width=True)

    st.markdown("### Capital Metrics")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Core Capital", fmt(K["ccap_c"]), delta=f"{K['ccap_c']-K['ccap_p']:+.4f}")
    with c2:
        st.metric("Total Capital", fmt(K["tcap_c"]), delta=f"{K['tcap_c']-K['tcap_p']:+.4f}")
    with c3:
        bv = K["tcap_c"] - cap_thr
        st.metric("Buffer", fmt(abs(bv)), delta="Above min" if bv > 0 else "Below min",
                  delta_color="normal" if bv > 0 else "inverse")

    if show_tbl:
        comp = [
            {"Parameter": "Gross NPA", "Value": fmt(K["gnpa_c"]), "Limit": f"{npa_thr:.1%}",
             "Status": "✓ Compliant" if K["gnpa_c"] <= npa_thr else "✗ Breach"},
            {"Parameter": "Net NPA", "Value": fmt(K["nnpa_c"]), "Limit": f"{npa_thr*0.8:.1%}",
             "Status": "✓ Compliant" if K["nnpa_c"] <= npa_thr * 0.8 else "✗ Breach"},
            {"Parameter": "Core Capital", "Value": fmt(K["ccap_c"]), "Limit": "5.50%",
             "Status": "✓ Compliant" if K["ccap_c"] >= 0.055 else "✗ Breach"},
            {"Parameter": "Total Capital", "Value": fmt(K["tcap_c"]), "Limit": f"{cap_thr:.1%}",
             "Status": "✓ Compliant" if K["tcap_c"] >= cap_thr else "✗ Breach"},
        ]
        st.dataframe(pd.DataFrame(comp), use_container_width=True, hide_index=True)

# ── Tab 4: Risk Scorecard (NEW) ──────────────────────────────
with tab4:
    st.markdown('<div class="sec-head"><span class="sec-icon">🗺️</span> Risk Scorecard</div>', unsafe_allow_html=True)

    # Build scorecard from all available metrics
    score_items = []
    for part in avail:
        s = get_series(part)
        if len(s) < 1:
            continue
        cur = s["Rs"].iloc[-1]
        # heuristic: treat as ratio if <= 2
        if is_ratio(cur):
            # lower is generally better for ratios (NPA, etc.)
            # use 0 as min, cur as val, some reasonable max
            bar_pct = min(cur / 0.15 * 100, 100) if cur > 0 else 0
            bar_color = "#059669" if cur < npa_thr else ("#D97706" if cur < npa_thr * 1.2 else "#DC2626")
        else:
            bar_pct = 50  # neutral for absolute values
            bar_color = "#2563EB"
        score_items.append({"metric": part, "value": fmt(cur), "bar_pct": bar_pct, "bar_color": bar_color})

    cols_per_row = 4
    for i in range(0, len(score_items), cols_per_row):
        row_items = score_items[i:i + cols_per_row]
        html_row = '<div class="scorecard-grid">'
        for item in row_items:
            html_row += f"""
            <div class="scorecard-item">
                <div class="scorecard-metric">{item['metric']}</div>
                <div class="scorecard-val">{item['value']}</div>
                <div class="scorecard-bar"><div class="scorecard-bar-fill" style="width:{item['bar_pct']}%;background:{item['bar_color']}"></div></div>
            </div>"""
        html_row += '</div>'
        st.markdown(html_row, unsafe_allow_html=True)

    st.markdown('<div class="sec-head"><span class="sec-icon">🔥</span> Heatmap — All Metrics × Periods</div>', unsafe_allow_html=True)
    if not avail:
        st.info("No metrics to display.")
    else:
        pivot = df.pivot_table(index="Particulars", columns="Month", values="Rs", aggfunc="first")
        # Normalize each row for color
        piv_norm = pivot.apply(lambda r: (r - r.min()) / (r.max() - r.min()) if r.max() != r.min() else 0.5, axis=1)

        fig_heat = go.Figure(data=go.Heatmap(
            z=piv_norm.values, x=piv_norm.columns, y=piv_norm.index,
            colorscale=[[0, "#D1FAE5"], [0.5, "#FEF3C7"], [1, "#FEE2E2"]],
            hovertemplate="%{y}<br>%{x}<br>Value: %{text}<extra></extra>",
            text=pivot.applymap(fmt).values,
            texttemplate="%{text}",
            textfont=dict(size=9, color="#0F172A"),
            xgap=2, ygap=2
        ))
        fig_heat.update_layout(height=max(300, len(avail) * 28), margin=dict(l=160, r=30, t=10, b=60),
                               xaxis=dict(tickangle=45, side="bottom", tickfont=dict(size=10)),
                               yaxis=dict(tickfont=dict(size=10)),
                               paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_heat, use_container_width=True)

# ── Tab 5: Data Explorer ────────────────────────────────────
with tab5:
    st.markdown('<div class="sec-head"><span class="sec-icon">📋</span> Interactive Explorer</div>', unsafe_allow_html=True)

    cf1, cf2 = st.columns(2)
    with cf1:
        pf = st.multiselect("Filter Particulars", options=avail, key="exp_filter")
    with cf2:
        sb = st.selectbox("Sort By", options=["Month", "Particulars", "Rs"], key="exp_sort")

    edf = df.copy()
    if pf:
        edf = edf[edf["Particulars"].isin(pf)]
    edf = edf.sort_values(by=[sb, "Month"])

    cd1, cd2 = st.columns(2)
    with cd1:
        rn = st.slider("Rows", 5, 100, 30, key="exp_rows")
    with cd2:
        st.download_button("📥 Export CSV", edf.to_csv(index=False), "mis_export.csv", "text/csv", key="dl")

    st.caption(f"Showing {min(rn, len(edf))} of {len(edf):,} records")
    if show_raw:
        st.dataframe(edf.head(rn), use_container_width=True, hide_index=True)

    st.markdown("### Pivot View")
    if not edf.empty:
        pvt = edf.pivot_table(index="Particulars", columns="Month", values="Rs", aggfunc="first")
        st.dataframe(pvt, use_container_width=True)

    with st.expander("📊 Dataset Profile"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Metrics", f"{df['Particulars'].nunique()}")
        c3.metric("Periods", f"{df['Month'].nunique()}")
        c4.metric("Range", f"{df['Month'].min()} → {df['Month'].max()}")

# ─────────────────────── Footer ───────────────────────
st.markdown("""<hr style="border:none;border-top:1px solid #E2E8F0;margin:2rem 0 1rem">
<div style="text-align:center;color:#94A3B8;font-size:.78rem;padding:.5rem 0">
    <strong style="color:#64748B">◆ Basel Analytics</strong> · Executive MIS Dashboard · Confidential<br>
    Generated {dt} · FY 2025-26
</div>""".format(dt=datetime.now().strftime("%d %b %Y %H:%M")), unsafe_allow_html=True)
