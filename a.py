"""
Executive MIS Dashboard  ·  Basel Analytics  ·  v4.1
Financial Risk Intelligence Platform
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

# ── DESIGN TOKENS ─────────────────────────────────────────────────────────────
BG    = "#05070F"
CARD  = "#0D1B3E"
CARD2 = "#091228"
BORD  = "#1E305A"
TEAL  = "#00D4AA"
BLUE  = "#3B82F6"
RED   = "#FF5C5C"
AMBER = "#F5A623"
WHITE = "#E8EDF5"
MUTED = "#8896B3"
PALETTE = [TEAL, BLUE, AMBER, RED, "#A855F7", "#EC4899", "#14B8A6", "#F97316"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

html,body,.stApp                   {{background:{BG}!important;}}
.main .block-container             {{padding:1.5rem 2rem 3rem;max-width:1680px;}}
*,*::before,*::after               {{box-sizing:border-box;}}
p,li,span,label,td,th,div          {{font-family:'Inter',sans-serif;color:{WHITE};}}

section[data-testid="stSidebar"]   {{background:#050C1E!important;border-right:1px solid {BORD}!important;}}
section[data-testid="stSidebar"] * {{color:{WHITE}!important;font-family:'Inter',sans-serif!important;}}
.sb-logo  {{font-family:'IBM Plex Mono',monospace!important;font-size:1.05rem;font-weight:700;color:{TEAL}!important;letter-spacing:-0.5px;margin:0;}}
.sb-tagline {{font-size:.63rem;letter-spacing:2px;text-transform:uppercase;color:{MUTED}!important;}}
.sb-sec {{font-size:.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{MUTED}!important;
          margin:1.1rem 0 .4rem;padding-bottom:.3rem;border-bottom:1px solid {BORD};}}

.dash-header {{background:linear-gradient(135deg,{CARD} 0%,{CARD2} 100%);
               border:1px solid {BORD};border-left:4px solid {TEAL};border-radius:12px;
               padding:1.75rem 2rem;margin-bottom:1.25rem;position:relative;overflow:hidden;}}
.dash-header::before {{content:'';position:absolute;top:-50%;right:-8%;width:380px;height:380px;
                        background:radial-gradient(circle,rgba(0,212,170,.07) 0%,transparent 68%);pointer-events:none;}}
.dash-eyebrow {{font-family:'IBM Plex Mono',monospace!important;font-size:.6rem;font-weight:700;
                letter-spacing:3px;text-transform:uppercase;color:{TEAL};margin-bottom:.4rem;}}
.dash-title   {{font-size:1.85rem;font-weight:800;color:{WHITE};margin:0 0 .25rem;line-height:1.15;}}
.dash-meta    {{display:flex;gap:2rem;flex-wrap:wrap;margin-top:.85rem;}}
.dash-meta span {{font-family:'IBM Plex Mono',monospace!important;font-size:.76rem;color:{MUTED};}}
.dash-meta strong {{color:{WHITE}!important;}}

.status-bar {{display:flex;gap:.7rem;flex-wrap:wrap;margin-bottom:1.2rem;}}
.s-pill {{display:inline-flex;align-items:center;gap:.4rem;padding:.32rem .8rem;border-radius:9999px;
          font-size:.66rem;font-weight:700;font-family:'IBM Plex Mono',monospace!important;
          letter-spacing:.5px;border:1px solid;}}
.s-pill.ok     {{background:rgba(0,212,170,.1);border-color:rgba(0,212,170,.35);color:{TEAL};}}
.s-pill.warn   {{background:rgba(245,166,35,.1);border-color:rgba(245,166,35,.35);color:{AMBER};}}
.s-pill.breach {{background:rgba(255,92,92,.1);border-color:rgba(255,92,92,.35);color:{RED};}}
.s-dot          {{width:6px;height:6px;border-radius:50%;flex-shrink:0;}}
.s-dot.ok      {{background:{TEAL};box-shadow:0 0 5px {TEAL};}}
.s-dot.warn    {{background:{AMBER};box-shadow:0 0 5px {AMBER};}}
.s-dot.breach  {{background:{RED};box-shadow:0 0 5px {RED};}}

.kpi-grid  {{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.2rem;}}
.kpi-card  {{background:{CARD};border:1px solid {BORD};border-radius:10px;padding:1.15rem 1.35rem;
             position:relative;overflow:hidden;transition:transform .18s,box-shadow .18s;}}
.kpi-card:hover {{transform:translateY(-3px);box-shadow:0 8px 28px rgba(0,0,0,.4);}}
.kpi-card::before {{content:'';position:absolute;top:0;left:0;width:3px;height:100%;border-radius:10px 0 0 10px;}}
.kpi-card.ok::before     {{background:{TEAL};}}
.kpi-card.warn::before   {{background:{AMBER};}}
.kpi-card.breach::before {{background:{RED};}}
.kpi-card.neutral::before {{background:{BORD};}}
.kpi-label {{font-size:.6rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{MUTED};margin-bottom:.5rem;}}
.kpi-val   {{font-family:'IBM Plex Mono',monospace!important;font-size:1.9rem;font-weight:700;
             color:{WHITE};line-height:1;margin-bottom:.4rem;}}
.kpi-delta {{font-family:'IBM Plex Mono',monospace!important;font-size:.73rem;}}
.kpi-delta.pos {{color:{TEAL};}}
.kpi-delta.neg {{color:{RED};}}
.kpi-delta.neu {{color:{MUTED};}}
.kpi-badge {{display:inline-flex;align-items:center;margin-top:.5rem;padding:.16rem .5rem;
             border-radius:9999px;font-size:.6rem;font-weight:700;
             font-family:'IBM Plex Mono',monospace!important;letter-spacing:.5px;}}
.kpi-badge.ok     {{background:rgba(0,212,170,.1);color:{TEAL};}}
.kpi-badge.warn   {{background:rgba(245,166,35,.1);color:{AMBER};}}
.kpi-badge.breach {{background:rgba(255,92,92,.1);color:{RED};}}

.alert         {{display:flex;align-items:flex-start;gap:.85rem;padding:.85rem 1.1rem;
                 border-radius:10px;margin-bottom:.6rem;border:1px solid;}}
.alert.danger  {{background:rgba(255,92,92,.07);border-color:rgba(255,92,92,.25);border-left:4px solid {RED};}}
.alert.warning {{background:rgba(245,166,35,.07);border-color:rgba(245,166,35,.25);border-left:4px solid {AMBER};}}
.alert.success {{background:rgba(0,212,170,.07);border-color:rgba(0,212,170,.25);border-left:4px solid {TEAL};}}
.alert-ico {{font-size:1.1rem;flex-shrink:0;line-height:1.5;}}
.alert-ttl {{font-weight:700;font-size:.83rem;color:{WHITE};margin-bottom:.12rem;}}
.alert-msg {{font-size:.76rem;color:{MUTED};}}

.sec-lbl {{font-family:'IBM Plex Mono',monospace!important;font-size:.6rem;font-weight:700;
           letter-spacing:2.5px;text-transform:uppercase;color:{TEAL};
           padding-bottom:.5rem;margin-bottom:.9rem;border-bottom:1px solid {BORD};}}

.stTabs [data-baseweb="tab-list"] {{background:{CARD}!important;border:1px solid {BORD};
                                    border-radius:10px;padding:.28rem;gap:.18rem;margin-bottom:1.2rem;}}
.stTabs [data-baseweb="tab"]      {{background:transparent!important;color:{MUTED}!important;
                                    border-radius:7px!important;padding:.42rem 1.05rem!important;
                                    font-size:.79rem!important;font-weight:600!important;
                                    border:none!important;transition:all .18s!important;}}
.stTabs [aria-selected="true"]    {{background:{TEAL}!important;color:{BG}!important;}}
.stTabs [data-baseweb="tab-panel"] {{padding:0!important;}}

.stSelectbox label,.stMultiSelect label,.stSlider label,
.stNumberInput label,.stCheckbox label {{color:{MUTED}!important;font-size:.79rem!important;}}
.stSelectbox [data-baseweb="select"]>div,
.stMultiSelect [data-baseweb="select"]>div {{background:{CARD}!important;border-color:{BORD}!important;color:{WHITE}!important;}}
div[data-testid="stMetric"]        {{background:{CARD};padding:.9rem;border-radius:10px;border:1px solid {BORD};}}
div[data-testid="stMetric"] label  {{color:{MUTED}!important;font-size:.75rem!important;}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{color:{WHITE}!important;font-family:'IBM Plex Mono',monospace!important;}}

.streamlit-expanderHeader  {{background:{CARD}!important;border:1px solid {BORD}!important;
                              border-radius:8px!important;color:{WHITE}!important;}}
.streamlit-expanderContent {{background:{CARD2}!important;border:1px solid {BORD}!important;border-top:none!important;}}

.stDownloadButton button {{background:rgba(0,212,170,.1)!important;border:1px solid rgba(0,212,170,.35)!important;
                           color:{TEAL}!important;border-radius:8px!important;font-size:.79rem!important;font-weight:600!important;}}
.stDownloadButton button:hover {{background:rgba(0,212,170,.2)!important;}}

#MainMenu,footer,header {{visibility:hidden;}}
hr {{border-color:{BORD}!important;}}
.stCaption p {{color:{MUTED}!important;font-size:.74rem!important;}}

@media(max-width:900px) {{.kpi-grid{{grid-template-columns:repeat(2,1fr);}}.dash-title{{font-size:1.4rem;}}}}
@media(max-width:600px) {{.kpi-grid{{grid-template-columns:1fr;}}.main .block-container{{padding:1rem;}}}}
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
        df.columns = (df.columns.str.strip()
                      .str.replace(r'\s+', ' ', regex=True)
                      .str.replace('\xa0', ' '))
        drop = [c for c in df.columns
                if c.startswith("Unnamed") or c in ("Helper","Rs.1","Rs.2","Movements(%)")]
        df.drop(columns=drop, errors="ignore", inplace=True)
        df["Month"]       = df["Month"].astype(str).str.strip()
        df["Particulars"] = df["Particulars"].astype(str).str.strip()
        df["Rs"]          = pd.to_numeric(df["Rs"], errors="coerce")
        return df
    except Exception:
        return None

df = load_data()
if df is None:
    st.error("⚠️ Failed to load data. Check your connection and refresh.")
    st.stop()


# ── LABEL DISCOVERY ───────────────────────────────────────────────────────────
def find_row(must_kws, prefer_kws=None):
    """
    Find a Particulars label matching ALL must_kws (case-insensitive).
    If prefer_kws given, among all matches prefer rows that also contain
    any of those words — useful when both 'amount' and 'ratio' rows exist.
    Falls back to first match if no preferred row found.
    """
    all_vals = df["Particulars"].dropna().unique()
    matches  = [v for v in all_vals
                if all(k.lower() in v.lower() for k in must_kws)]
    if not matches:
        return None
    if prefer_kws:
        preferred = [v for v in matches
                     if any(k.lower() in v.lower() for k in prefer_kws)]
        if preferred:
            return preferred[0]
    return matches[0]

LBL = {
    # For capital rows, prefer 'ratio'/'adequacy'/'car'/'%' labels
    # so we pick the ratio row, not the absolute-amount row
    "gross_npa":  find_row(["gross", "npa"]),
    "net_npa":    find_row(["net",   "npa"]),
    "core_cap":   find_row(["core",  "capital"], prefer_kws=["ratio", "%", "tier"]),
    "total_cap":  find_row(["total", "capital"],
                           prefer_kws=["ratio", "adequacy", "car", "%"]),
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
    """Return Month/Rs series, optionally filtered to a list of months.
    FIX: months parameter is what wires the comparison_periods slider."""
    s = df[df["Particulars"] == label][["Month","Rs"]].dropna(subset=["Rs"]).copy()
    if months is not None:
        s = s[s["Month"].isin(months)]
    return s.reset_index(drop=True)

def prev_month_of(month, months_list):
    idx = months_list.index(month) if month in months_list else 0
    return months_list[max(0, idx - 1)]

def is_ratio(v):
    return abs(v) <= 2.0

def fmt(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v:.2%}" if is_ratio(v) else f"{v:,.2f}"

def pct_chg(cur, prv):
    if prv is None or abs(prv) < 1e-9:
        return None
    return ((cur - prv) / abs(prv)) * 100

def get_status(v, thr, lower_better=True):
    if lower_better:
        if v <= thr:           return "ok"
        elif v <= thr * 1.25:  return "warn"
        return "breach"
    else:
        if v >= thr:           return "ok"
        elif v >= thr * 0.8:   return "warn"
        return "breach"


# ── PLOTLY DARK LAYOUT ────────────────────────────────────────────────────────
# NOTE: _PLOT_BASE intentionally omits xaxis / yaxis / legend so that
#       callers can pass those in kwargs or via update_xaxes/update_yaxes
#       without triggering "got multiple values for keyword argument" TypeError.
_PLOT_BASE = dict(
    paper_bgcolor = CARD,
    plot_bgcolor  = BG,
    font          = dict(color=WHITE, family="Inter", size=11),
    hoverlabel    = dict(bgcolor=CARD2, bordercolor=BORD, font=dict(color=WHITE, size=12)),
    hovermode     = "x unified",
    margin        = dict(l=20, r=20, t=45, b=65),
)

def apply_dark(fig, height=380, **kwargs):
    """
    Apply dark theme to a figure.
    Pass per-chart overrides (title, legend, margin, etc.) via kwargs.
    xaxis / yaxis styling is handled by update_xaxes / update_yaxes below
    so there is NEVER a duplicate-key conflict.
    """
    fig.update_layout(height=height, **_PLOT_BASE, **kwargs)
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor=BORD,
        linecolor=BORD, tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor=BORD,
        linecolor=BORD, tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    return fig

def apply_dark_subplot(fig, height=340):
    """Same as apply_dark but for subplot figures (update_*axes touches all)."""
    fig.update_layout(height=height, **_PLOT_BASE, showlegend=False)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BORD,
                     linecolor=BORD, tickfont=dict(color=MUTED))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=BORD,
                     linecolor=BORD, tickfont=dict(color=MUTED))
    # Subplot titles live in layout.annotations — make them visible
    fig.update_annotations(font=dict(color=MUTED, size=12))
    return fig

def dark_gauge(value, max_val, title, threshold, lower_better=True):
    v  = value * 100     if is_ratio(value)     else value
    t  = threshold * 100 if is_ratio(threshold) else threshold
    m  = max_val * 100   if is_ratio(max_val)   else max_val
    mx = m * 1.55

    st_cls = get_status(value, threshold, lower_better)
    bar_c  = TEAL if st_cls == "ok" else (AMBER if st_cls == "warn" else RED)

    if lower_better:
        steps = [{"range": [0, t],         "color": "rgba(0,212,170,.12)"},
                 {"range": [t, t * 1.25],  "color": "rgba(245,166,35,.12)"},
                 {"range": [t * 1.25, mx], "color": "rgba(255,92,92,.12)"}]
    else:
        steps = [{"range": [0, t * 0.8],   "color": "rgba(255,92,92,.12)"},
                 {"range": [t * 0.8, t],   "color": "rgba(245,166,35,.12)"},
                 {"range": [t, mx],        "color": "rgba(0,212,170,.12)"}]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=v,
        gauge=dict(
            axis=dict(range=[0, mx], tickcolor=MUTED, tickfont=dict(color=MUTED, size=9)),
            bar=dict(color=bar_c, thickness=0.6),
            bgcolor=BG, bordercolor=BORD, borderwidth=1,
            steps=steps,
            threshold=dict(line=dict(color=RED, width=2.5), thickness=0.8, value=t),
        ),
        number=dict(suffix="%", font=dict(size=24, color=WHITE, family="IBM Plex Mono")),
        title=dict(text=title, font=dict(size=11, color=MUTED, family="Inter")),
    ))
    fig.update_layout(
        height=210, paper_bgcolor=CARD, plot_bgcolor=BG,
        margin=dict(l=20, r=20, t=28, b=18),
        font=dict(color=WHITE),
    )
    return fig


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.1rem 0 1rem;border-bottom:1px solid {BORD};">
      <p class="sb-logo">BASEL<span style="color:{WHITE}">ANALYTICS</span></p>
      <p class="sb-tagline">Risk Intelligence Platform</p>
    </div>""", unsafe_allow_html=True)

    all_months  = df["Month"].dropna().unique().tolist()
    avail_parts = df["Particulars"].dropna().unique().tolist()

    st.markdown('<p class="sb-sec">Reporting Period</p>', unsafe_allow_html=True)
    selected_month = st.selectbox("Period", all_months,
                                  index=len(all_months) - 1,
                                  label_visibility="collapsed")
    pm = prev_month_of(selected_month, all_months)
    st.caption(f"Prior period → **{pm}**")

    st.markdown('<p class="sb-sec">Metric Selection</p>', unsafe_allow_html=True)
    selected_parts = st.multiselect(
        "Metrics", avail_parts,
        default=avail_parts[:4] if len(avail_parts) >= 4 else avail_parts,
        label_visibility="collapsed",
    )

    # ── FIX 1: comparison_periods — wired to recent_months used everywhere ────
    st.markdown('<p class="sb-sec">Analysis Window</p>', unsafe_allow_html=True)
    comparison_periods = st.slider(
        "Last N Periods",
        min_value=2,
        max_value=min(12, len(all_months)),
        value=6,
        label_visibility="collapsed",
    )
    st.caption(f"Showing last **{comparison_periods}** periods in all charts & tables")

    # ── FIX 2 & 3: checkboxes with clear, correct scope ──────────────────────
    st.markdown('<p class="sb-sec">Display Options</p>', unsafe_allow_html=True)
    show_tables = st.checkbox(
        "Show Analysis Tables",
        value=True,
        help="Toggles summary/compliance tables in Tabs 1, 2 and 3",
    )
    show_raw = st.checkbox(
        "Show Raw Data Table",
        value=False,
        help="Reveals the complete unfiltered dataset in the Data Explorer tab",
    )

    st.markdown('<p class="sb-sec">Compliance Thresholds</p>', unsafe_allow_html=True)
    npa_threshold = st.number_input("NPA Warning (%)",   value=5.0, step=0.5, format="%.1f") / 100
    cap_threshold = st.number_input("Capital Floor (%)", value=8.5, step=0.5, format="%.1f") / 100

    st.markdown('<p class="sb-sec">System</p>', unsafe_allow_html=True)
    st.caption(f"🕒 {datetime.now().strftime('%Y-%m-%d  %H:%M')}")
    st.caption(f"📦 {len(df):,} records · {len(all_months)} periods")


# ── FIX 1: derived window — used in EVERY chart / series call below ───────────
recent_months = all_months[-comparison_periods:]

# ── KPI VALUES ────────────────────────────────────────────────────────────────
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
<div class="dash-header">
  <div class="dash-eyebrow">Basel III Compliance Monitoring</div>
  <h1 class="dash-title">Executive MIS Dashboard</h1>
  <div class="dash-meta">
    <span>📅 Period&nbsp;<strong>{selected_month}</strong></span>
    <span>📆 Prior&nbsp;<strong>{pm}</strong></span>
    <span>🔍 Window&nbsp;<strong>Last {comparison_periods} periods</strong></span>
    <span>🗄️ Records&nbsp;<strong>{len(df):,}</strong></span>
  </div>
</div>""", unsafe_allow_html=True)

# ── COMPLIANCE STATUS BAR ─────────────────────────────────────────────────────
def s_pill(label, val, thr, lower_better=True):
    cls  = get_status(val, thr, lower_better)
    tags = {"ok": "COMPLIANT", "warn": "WARNING", "breach": "BREACH"}
    return (f'<div class="s-pill {cls}">'
            f'<span class="s-dot {cls}"></span>'
            f'{label}&nbsp;{fmt(val)}&nbsp;—&nbsp;{tags[cls]}</div>')

st.markdown(
    '<div class="status-bar">'
    + s_pill("Gross NPA",     kpi["gnpa_c"], npa_threshold,       lower_better=True)
    + s_pill("Net NPA",       kpi["nnpa_c"], npa_threshold * 0.8, lower_better=True)
    + s_pill("Core Capital",  kpi["core_c"], 0.055,               lower_better=False)
    + s_pill("Total Capital", kpi["tot_c"],  cap_threshold,       lower_better=False)
    + '</div>',
    unsafe_allow_html=True,
)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
def kpi_card_html(label, cur, prv, lower_better=True, thr=None):
    delta = cur - prv
    zero  = abs(delta) < 1e-9
    cls   = get_status(cur, thr, lower_better) if thr is not None else "neutral"
    blbl  = {"ok": "✓ COMPLIANT", "warn": "⚠ WARNING", "breach": "✗ BREACH"}
    badge = f'<div class="kpi-badge {cls}">{blbl[cls]}</div>' if thr else ""

    if zero:
        dcls, dtxt = "neu", "— no change"
    else:
        up   = delta > 0
        good = (up and not lower_better) or (not up and lower_better)
        dcls = "pos" if good else "neg"
        arrow = "▲" if up else "▼"
        p     = pct_chg(cur, prv)
        pstr  = f"{abs(p):.2f}%" if p is not None else fmt(abs(delta))
        dtxt  = f"{arrow} {pstr} vs prior"

    return (f'<div class="kpi-card {cls}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-val">{fmt(cur)}</div>'
            f'<div class="kpi-delta {dcls}">{dtxt}</div>'
            f'{badge}</div>')

st.markdown(
    '<div class="kpi-grid">'
    + kpi_card_html("Gross NPA",        kpi["gnpa_c"], kpi["gnpa_p"], True,  npa_threshold)
    + kpi_card_html("Net NPA",          kpi["nnpa_c"], kpi["nnpa_p"], True,  npa_threshold * 0.8)
    + kpi_card_html("Core Capital",     kpi["core_c"], kpi["core_p"], False, 0.055)
    + kpi_card_html("Capital Adequacy", kpi["tot_c"],  kpi["tot_p"],  False, cap_threshold)
    + '</div>',
    unsafe_allow_html=True,
)

# ── ALERT BANNERS ─────────────────────────────────────────────────────────────
def alert_html(level, icon, title, msg):
    return (f'<div class="alert {level}">'
            f'<div class="alert-ico">{icon}</div>'
            f'<div><div class="alert-ttl">{title}</div>'
            f'<div class="alert-msg">{msg}</div></div></div>')

alerts = ""
if kpi["gnpa_c"] > npa_threshold:
    alerts += alert_html("danger", "🚨", "Gross NPA Breach",
        f"Current {fmt(kpi['gnpa_c'])} exceeds regulatory threshold of {fmt(npa_threshold)}.")
elif kpi["gnpa_c"] > npa_threshold * 0.85:
    alerts += alert_html("warning", "⚠️", "Gross NPA Approaching Limit",
        f"{fmt(kpi['gnpa_c'])} is within 15% of the {fmt(npa_threshold)} threshold.")

if kpi["tot_c"] < cap_threshold:
    alerts += alert_html("danger", "🚨", "Capital Adequacy Breach",
        f"Total Capital {fmt(kpi['tot_c'])} is below regulatory minimum {fmt(cap_threshold)}.")
elif kpi["tot_c"] < cap_threshold * 1.2:
    alerts += alert_html("warning", "⚠️", "Capital Buffer Eroding",
        f"{fmt(kpi['tot_c'])} is approaching the {fmt(cap_threshold)} regulatory floor.")

if not alerts:
    alerts = alert_html("success", "✅", "All Metrics Within Regulatory Limits",
        f"No compliance breaches detected as of {selected_month}.")

st.markdown(alerts, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Performance",
    "📉  Asset Quality",
    "🛡️  Capital",
    "🗃️  Data Explorer",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Performance
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="sec-lbl">Multi-Metric Performance Trend</div>',
                unsafe_allow_html=True)

    if not selected_parts:
        st.info("Select metrics in the sidebar to populate this chart.")
    else:
        trend_df = (df[df["Particulars"].isin(selected_parts)]
                      .pipe(lambda d: d[d["Month"].isin(recent_months)])   # FIX 1
                      .copy())

        fig_trend = px.line(trend_df, x="Month", y="Rs", color="Particulars",
                            markers=True, color_discrete_sequence=PALETTE)
        fig_trend.update_traces(mode="lines+markers",
                                marker=dict(size=8), line=dict(width=2.5))
        # No xaxis/yaxis in apply_dark kwargs → zero conflict risk
        apply_dark(fig_trend, height=390,
                   xaxis_title="Period",
                   yaxis_title="Value",
                   legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center",
                               bgcolor="rgba(0,0,0,0)", bordercolor=BORD,
                               font=dict(color=WHITE)))
        st.plotly_chart(fig_trend, use_container_width=True)

    # NPA side-by-side area charts
    st.markdown('<div class="sec-lbl">NPA Period-over-Period</div>',
                unsafe_allow_html=True)

    gnpa_s = get_series(LBL["gross_npa"], recent_months)   # FIX 1
    nnpa_s = get_series(LBL["net_npa"],   recent_months)   # FIX 1

    fig2 = make_subplots(rows=1, cols=2,
                         subplot_titles=("Gross NPA", "Net NPA"),
                         horizontal_spacing=0.12)
    fig2.add_trace(go.Scatter(
        x=gnpa_s["Month"], y=gnpa_s["Rs"], name="Gross NPA",
        fill="tozeroy", mode="lines+markers",
        line=dict(color=TEAL, width=2.5), fillcolor="rgba(0,212,170,.14)",
        marker=dict(size=7, color=TEAL),
    ), row=1, col=1)
    fig2.add_trace(go.Scatter(
        x=nnpa_s["Month"], y=nnpa_s["Rs"], name="Net NPA",
        fill="tozeroy", mode="lines+markers",
        line=dict(color=BLUE, width=2.5), fillcolor="rgba(59,130,246,.14)",
        marker=dict(size=7, color=BLUE),
    ), row=1, col=2)
    for col in (1, 2):
        fig2.add_hline(y=npa_threshold, line_dash="dash", line_color=RED,
                       line_width=1.5,
                       annotation_text=f"Threshold {fmt(npa_threshold)}",
                       annotation_font=dict(color=RED, size=10),
                       row=1, col=col)
    apply_dark_subplot(fig2, height=330)
    st.plotly_chart(fig2, use_container_width=True)

    # FIX 2: show_tables gates summary table
    if show_tables:
        st.markdown('<div class="sec-lbl">Key Metrics Summary</div>',
                    unsafe_allow_html=True)
        rows = []
        for lbl, key in [("Gross NPA","gross_npa"), ("Net NPA","net_npa"),
                         ("Core Capital","core_cap"), ("Total Capital","total_cap")]:
            s = get_series(LBL[key], recent_months)           # FIX 1
            if len(s) >= 2:
                cur, prv = s["Rs"].iloc[-1], s["Rs"].iloc[-2]
                p = pct_chg(cur, prv)
                chg = f"{p:+.2f}%" if p is not None else "N/A"
            elif len(s) == 1:
                cur, prv, chg = s["Rs"].iloc[-1], None, "N/A"
            else:
                continue
            rows.append({
                "Metric":   lbl,
                "Current":  fmt(cur),
                "Previous": fmt(prv) if prv is not None else "N/A",
                "Change":   chg,
                "Min":      fmt(s["Rs"].min()),
                "Max":      fmt(s["Rs"].max()),
                "Average":  fmt(s["Rs"].mean()),
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Asset Quality
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-lbl">Asset Quality Dashboard</div>',
                unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(
            dark_gauge(kpi["gnpa_c"], 0.15, "Gross NPA Ratio",
                       npa_threshold, lower_better=True),
            use_container_width=True)
    with g2:
        st.plotly_chart(
            dark_gauge(kpi["nnpa_c"], 0.10, "Net NPA Ratio",
                       npa_threshold * 0.8, lower_better=True),
            use_container_width=True)

    with st.expander("📚 NPA Classification — Basel III Reference"):
        st.markdown("""
| Category | Definition | Provisioning |
|---|---|---|
| **Standard** | Timely repayment | 0.25% – 2.00% |
| **Sub-Standard** | NPA > 90 days | 15% – 25% |
| **Doubtful** | NPA > 12 months | 25% – 100% |
| **Loss** | Non-recoverable | 100% |
""")

    st.markdown('<div class="sec-lbl">NPA Trend Analysis</div>',
                unsafe_allow_html=True)

    gnpa_s = get_series(LBL["gross_npa"], recent_months)   # FIX 1
    nnpa_s = get_series(LBL["net_npa"],   recent_months)   # FIX 1

    fig_npa = go.Figure()
    fig_npa.add_trace(go.Bar(
        x=gnpa_s["Month"], y=gnpa_s["Rs"], name="Gross NPA",
        marker_color=TEAL, marker_opacity=0.85,
        text=gnpa_s["Rs"].apply(fmt), textposition="outside",
        textfont=dict(color=WHITE, size=9),
    ))
    fig_npa.add_trace(go.Scatter(
        x=nnpa_s["Month"], y=nnpa_s["Rs"], name="Net NPA",
        mode="lines+markers+text",
        line=dict(color=RED, width=2.5), marker=dict(size=9, color=RED),
        text=nnpa_s["Rs"].apply(fmt), textposition="top center",
        textfont=dict(color=RED, size=9),
    ))
    fig_npa.add_hline(y=npa_threshold, line_dash="dash", line_color=AMBER,
                      line_width=1.5,
                      annotation_text=f"Threshold  {fmt(npa_threshold)}",
                      annotation_font=dict(color=AMBER, size=10))
    apply_dark(fig_npa, height=370,
               xaxis_title="Period", yaxis_title="NPA Ratio",
               barmode="group",
               legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center",
                           bgcolor="rgba(0,0,0,0)", font=dict(color=WHITE)))
    st.plotly_chart(fig_npa, use_container_width=True)

    # FIX 2: show_tables gates this table
    if show_tables:
        st.markdown('<div class="sec-lbl">NPA Data Table</div>',
                    unsafe_allow_html=True)
        merged = gnpa_s.merge(nnpa_s, on="Month", suffixes=("_g", "_n"))
        merged.columns = ["Period", "_g", "_n"]
        merged["Gross NPA"] = merged["_g"].apply(fmt)
        merged["Net NPA"]   = merged["_n"].apply(fmt)
        merged["Spread"]    = (merged["_g"] - merged["_n"]).apply(fmt)
        st.dataframe(merged[["Period","Gross NPA","Net NPA","Spread"]],
                     use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Capital
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-lbl">Capital Adequacy & Compliance</div>',
                unsafe_allow_html=True)

    buffer_val = kpi["tot_c"] - cap_threshold

    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(
            dark_gauge(kpi["core_c"], 0.15, "Core Capital (Tier I)",
                       0.055, lower_better=False),
            use_container_width=True)
    with g2:
        st.plotly_chart(
            dark_gauge(kpi["tot_c"], 0.20, "Total Capital Ratio",
                       cap_threshold, lower_better=False),
            use_container_width=True)
    with g3:
        st.plotly_chart(
            dark_gauge(abs(buffer_val), cap_threshold * 0.5, "Capital Buffer",
                       cap_threshold * 0.1, lower_better=False),
            use_container_width=True)

    st.markdown('<div class="sec-lbl">Capital Position Over Time</div>',
                unsafe_allow_html=True)

    core_s  = get_series(LBL["core_cap"],  recent_months)   # FIX 1
    total_s = get_series(LBL["total_cap"], recent_months)   # FIX 1

    fig_cap = go.Figure()
    fig_cap.add_trace(go.Scatter(
        x=core_s["Month"], y=core_s["Rs"],
        name="Core Capital (Tier I)", fill="tozeroy", mode="lines+markers",
        line=dict(color=BLUE, width=2.5), fillcolor="rgba(59,130,246,.14)",
        marker=dict(size=8),
    ))
    fig_cap.add_trace(go.Scatter(
        x=total_s["Month"], y=total_s["Rs"],
        name="Total Capital", fill="tonexty", mode="lines+markers",
        line=dict(color=TEAL, width=2.5), fillcolor="rgba(0,212,170,.14)",
        marker=dict(size=8),
    ))
    fig_cap.add_hline(y=cap_threshold, line_dash="dash", line_color=RED,
                      line_width=1.5,
                      annotation_text=f"Regulatory Min  {fmt(cap_threshold)}",
                      annotation_font=dict(color=RED, size=10),
                      annotation_position="bottom right")
    apply_dark(fig_cap, height=370,
               xaxis_title="Period", yaxis_title="Capital Ratio",
               legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center",
                           bgcolor="rgba(0,0,0,0)", font=dict(color=WHITE)))
    st.plotly_chart(fig_cap, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        d = kpi["core_c"] - kpi["core_p"]
        st.metric("Core Capital (Tier I)",  fmt(kpi["core_c"]), delta=f"{d:+.4f}")
    with m2:
        d = kpi["tot_c"] - kpi["tot_p"]
        st.metric("Total Capital Ratio",    fmt(kpi["tot_c"]),  delta=f"{d:+.4f}")
    with m3:
        st.metric("Capital Buffer", fmt(abs(buffer_val)),
                  delta="Above minimum" if buffer_val >= 0 else "Below minimum",
                  delta_color="normal" if buffer_val >= 0 else "inverse")

    # FIX 2: show_tables gates compliance report
    if show_tables:
        st.markdown('<div class="sec-lbl">Compliance Status Report</div>',
                    unsafe_allow_html=True)
        comp = [
            {"Parameter": "Gross NPA",     "Current": fmt(kpi["gnpa_c"]),
             "Threshold": fmt(npa_threshold),
             "Status": "✓ Compliant" if kpi["gnpa_c"] <= npa_threshold else "✗ Breach"},
            {"Parameter": "Net NPA",       "Current": fmt(kpi["nnpa_c"]),
             "Threshold": fmt(npa_threshold * 0.8),
             "Status": "✓ Compliant" if kpi["nnpa_c"] <= npa_threshold * 0.8 else "✗ Breach"},
            {"Parameter": "Core Capital",  "Current": fmt(kpi["core_c"]),
             "Threshold": "5.50%",
             "Status": "✓ Compliant" if kpi["core_c"] >= 0.055 else "✗ Breach"},
            {"Parameter": "Total Capital", "Current": fmt(kpi["tot_c"]),
             "Threshold": fmt(cap_threshold),
             "Status": "✓ Compliant" if kpi["tot_c"] >= cap_threshold else "✗ Breach"},
        ]
        st.dataframe(pd.DataFrame(comp), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Data Explorer
# FIX 3: explorer_df is ALWAYS visible; show_raw adds the full unfiltered df
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-lbl">Interactive Data Explorer</div>',
                unsafe_allow_html=True)

    cf1, cf2 = st.columns(2)
    with cf1:
        part_filter = st.multiselect("Filter by Metric", avail_parts,
                                     key="explorer_filter")
    with cf2:
        sort_col = st.selectbox("Sort By", ["Month","Particulars","Rs"],
                                key="explorer_sort")

    # Build filtered + windowed view
    explorer_df = df[df["Month"].isin(recent_months)].copy()   # FIX 1
    if part_filter:
        explorer_df = explorer_df[explorer_df["Particulars"].isin(part_filter)]
    explorer_df = explorer_df.sort_values([sort_col, "Month"])

    r1, r2 = st.columns([3, 1])
    with r1:
        rows_to_show = st.slider("Rows to display", 5, 200, 25, key="rows_slider")
    with r2:
        st.download_button(
            "📥 Export CSV", explorer_df.to_csv(index=False),
            "mis_export.csv", "text/csv", key="csv_dl",
        )

    st.caption(
        f"{min(rows_to_show, len(explorer_df))} of {len(explorer_df)} records  "
        f"·  {comparison_periods} periods  "
        f"·  {explorer_df['Particulars'].nunique()} metrics"
    )

    # ── Always visible: filtered / windowed table ──────────────────────────────
    st.markdown('<div class="sec-lbl">Filtered Data</div>', unsafe_allow_html=True)
    if explorer_df.empty:
        st.info("No records match the current filters.")
    else:
        st.dataframe(explorer_df.head(rows_to_show),
                     use_container_width=True, hide_index=True)

    # ── Always visible: pivot table ───────────────────────────────────────────
    st.markdown('<div class="sec-lbl">Pivot — Metrics × Periods</div>',
                unsafe_allow_html=True)
    if not explorer_df.empty:
        pivot = explorer_df.pivot_table(
            index="Particulars", columns="Month", values="Rs", aggfunc="first")
        st.dataframe(pivot, use_container_width=True)

    # ── FIX 3: show_raw → full unfiltered dataset (not the filtered view) ─────
    if show_raw:
        st.markdown('<div class="sec-lbl">Raw — Complete Unfiltered Dataset</div>',
                    unsafe_allow_html=True)
        st.caption(f"All {len(df):,} records across all periods and metrics.")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("📊 Dataset Statistics"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Records",   f"{len(df):,}")
        c2.metric("Unique Metrics",  f"{df['Particulars'].nunique()}")
        c3.metric("All Periods",     f"{df['Month'].nunique()}")
        c4.metric("Current Window",  f"{comparison_periods}")


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<div style="text-align:center;color:{MUTED};font-size:.75rem;padding:.65rem 0;'
    f'font-family:\'IBM Plex Mono\',monospace;">'
    f'BASEL ANALYTICS &nbsp;·&nbsp; Executive MIS Dashboard &nbsp;·&nbsp; FY 2025-26'
    f'&nbsp;·&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    f'</div>',
    unsafe_allow_html=True,
)
