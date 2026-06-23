"""
Basel III Regulatory Reporting Dashboard
Nepal Banking Sector — Streamlit Application
Reads baseldata.xlsx and presents interactive compliance analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re

# ================================================================
# 1. PAGE CONFIGURATION
# ================================================================
st.set_page_config(
    page_title="Basel III Dashboard — NRB Compliance",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ──────────────────────────────────────────────────────
C = {
    "bg":       "#0B0F19",
    "card":     "#111827",
    "card2":    "#1A2236",
    "border":   "#1E2D4A",
    "text":     "#E2E8F0",
    "muted":    "#64748B",
    "green":    "#10B981",
    "cyan":     "#06B6D4",
    "amber":    "#F59E0B",
    "red":      "#EF4444",
    "purple":   "#8B5CF6",
    "blue":     "#3B82F6",
    "pink":     "#EC4899",
}

RATIO_KEYS = {"cet1_ratio", "total_car", "gross_npa_ratio", "net_npa_ratio"}

# NRB reference minimums (Basel III + NRB buffers)
NRB_CET1_MIN  = 8.0
NRB_TOTAL_MIN = 11.0

# ================================================================
# 2. CUSTOM CSS
# ================================================================
def inject_css():
    st.markdown(f"""<style>
    /* ── Global ────────────────────────────────────── */
    .stApp {{ background-color: {C["bg"]}; color: {C["text"]}; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {C["card"]} 0%, #0D1321 100%);
        border-right: 1px solid {C["border"]};
    }}
    [data-testid="stSidebar"] * {{ color: {C["muted"]} !important; }}
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{ color: {C["text"]} !important; }}

    /* ── Tabs ─────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px; background: transparent; border-bottom: 1px solid {C["border"]};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0; padding: 10px 20px;
        background: transparent; color: {C["muted"]};
        font-size: 13px; font-weight: 500;
        transition: all .2s;
    }}
    .stTabs [aria-selected="true"] {{
        background: {C["card2"]}; color: {C["green"]};
        border-bottom: 2px solid {C["green"]};
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {C["green"]} !important; height: 2px !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{ background: transparent; padding-top: 20px; }}

    /* ── Metrics ──────────────────────────────────── */
    [data-testid="stMetricValue"] {{
        font-size: 26px !important; font-weight: 700 !important;
        font-family: 'Segoe UI', system-ui, sans-serif !important;
        letter-spacing: -0.5px;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 12px !important; color: {C["muted"]} !important;
        text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
    }}
    [data-testid="stMetricDelta"] {{ font-size: 13px !important; }}

    /* ── Dataframe ────────────────────────────────── */
    .stDataFrame {{
        border: 1px solid {C["border"]}; border-radius: 12px;
        background: {C["card"]}; overflow: hidden;
    }}
    .stDataFrame thead th {{
        background: {C["card2"]}; color: {C["muted"]};
        font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
        border-bottom: 1px solid {C["border"]}; padding: 12px 16px;
    }}
    .stDataFrame td {{
        color: {C["text"]}; font-size: 13px; padding: 10px 16px;
        border-bottom: 1px solid rgba(30,45,74,0.4);
    }}
    .stDataFrame tr:hover td {{ background: rgba(255,255,255,0.02); }}

    /* ── KPI Card Grid ────────────────────────────── */
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 16px; }}
    .kpi-card {{
        background: {C["card"]}; border: 1px solid {C["border"]};
        border-radius: 14px; padding: 20px; position: relative; overflow: hidden;
        transition: transform .2s, box-shadow .2s;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        border-color: {C["border"]};
    }}
    .kpi-card .kpi-glow {{
        position: absolute; top: -30px; right: -30px;
        width: 100px; height: 100px; border-radius: 50%;
        filter: blur(50px); opacity: 0.1; pointer-events: none;
    }}
    .kpi-card .kpi-icon {{
        width: 38px; height: 38px; border-radius: 10px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 16px; margin-bottom: 14px;
    }}
    .kpi-card .kpi-label {{
        font-size: 11px; color: {C["muted"]}; text-transform: uppercase;
        letter-spacing: 0.8px; font-weight: 600; margin-bottom: 6px;
    }}
    .kpi-card .kpi-val {{
        font-size: 28px; font-weight: 800; letter-spacing: -0.5px;
        font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.1;
    }}
    .kpi-card .kpi-sub {{
        font-size: 11px; margin-top: 6px; font-weight: 600;
    }}
    .kpi-card .kpi-bar {{
        height: 4px; border-radius: 2px; background: rgba(255,255,255,0.06);
        margin-top: 12px; overflow: hidden;
    }}
    .kpi-card .kpi-bar-fill {{
        height: 100%; border-radius: 2px; transition: width .8s ease;
    }}

    /* ── Status Banner ────────────────────────────── */
    .status-banner {{
        padding: 12px 18px; border-radius: 10px;
        display: flex; align-items: center; gap: 10px;
        font-size: 13px; font-weight: 500; margin-bottom: 24px;
    }}
    .status-dot {{
        width: 8px; height: 8px; border-radius: 50%; position: relative;
    }}
    .status-dot::after {{
        content: ''; position: absolute; inset: -4px; border-radius: 50%;
        border: 1.5px solid currentColor; opacity: 0;
        animation: ping 2s cubic-bezier(0,0,0.2,1) infinite;
    }}
    @keyframes ping {{
        0% {{ transform: scale(1); opacity: .5; }}
        100% {{ transform: scale(2); opacity: 0; }}
    }}

    /* ── Section Header ───────────────────────────── */
    .section-head {{
        font-size: 15px; font-weight: 700; color: {C["text"]};
        margin-bottom: 16px; padding-left: 12px;
        border-left: 3px solid {C["green"]};
    }}

    /* ── Scrollbar ────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {C["border"]}; border-radius: 3px; }}

    /* ── Hide default Streamlit elements ──────────── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: rgba(11,15,25,0.8) !important;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid {C["border"]};
    }}
    </style>""", unsafe_allow_html=True)


# ================================================================
# 3. DATA LOADING & PARSING
# ================================================================
def parse_rs(val):
    """Convert Rs column to float. Handles '-', '(neg)', '15.46%', commas."""
    if pd.isna(val) or str(val).strip() in ("-", "", "nan"):
        return np.nan
    s = str(val).strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    if "%" in s:
        return float(s.replace("%", ""))
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


# Metric definitions: key → list of possible Particulars names
METRIC_MAP = {
    "paid_up_capital":       ["Paid Up Equity Share Capital"],
    "share_premium":         ["Share Premium"],
    "statutory_reserves":    ["Statutory General Reserves"],
    "retained_earnings":     ["Retained Earnings"],
    "cumulative_profit":     ["Un-Audited Current Year Cumulative Profit"],
    "cap_adj_reserve":       ["Capital Adjustment Reserve"],
    "core_capital":          ["Core Capital (Tier 1)"],
    "gen_llp":               ["General Loan Loss Provision"],
    "exch_reserves":         ["Exchange Equalization Reserves"],
    "inv_adj_reserve":       ["Investment Adjustment Reserve"],
    "sub_debt":              ["Subordinated Term Debt"],
    "tier2_capital":         [
        "Supplementary Capital (Tier 2)",
        "Eligible Supplementary Capital (Tier 2)",
    ],
    "total_capital_fund":    ["Total Qualifying Capital (Total Capital Fund)"],
    "cet1_ratio":            ["Capital Adequacy Ratio \u2013 Core Capital"],
    "total_car":             ["Capital Adequacy Ratio \u2013 Total Capital Fund"],
    "rwe_credit":            ["Risk Weighted Exposure For Credit Risk"],
    "rwe_operational":       ["Risk Weighted Exposure For Operational Risk"],
    "rwe_market":            ["Risk Weighted Exposure For Market Risk"],
    "pillar2_adj":           ["Adjustments Under Pillar Ii"],
    "rwe_cap_charge":        [
        "Add Rwe Equvalent To Reciprocal Of Capital Charge Of 3 % Of Gross Income.",
        "Add Rwe Equvalent To Reciprocal Of Capital Charge",
        "Add Rwe Equivalent To Reciprocal Of Capital Charge",
    ],
    "risk_mgmt_adj":         [
        "Overall Risk Management Policies And Precedures Are Not Satisfactory"
    ],
    "nla_shortfall":         ["Net Liquid Assets To Total Deposit Ratio Is Shortfall"],
    "rwe_total":             [
        "Total Risk Weighted Exposures (A+B+C+D)",
        "Total Risk Weighted Exposures (A+B+C)",
    ],
    # Credit portfolio
    "cl_govt":               ["Claims On Government And Central Bank"],
    "cl_banks":              ["Claims On Banks"],
    "cl_corporate":          ["Claims On Corporate And Securities Firm"],
    "cl_retail":             ["Claims On Regulatory Retail Portfolio"],
    "cl_residential":        ["Claim Secured By Residential Properties"],
    "cl_commercial_re":      ["Claims Secured By Commercial Real State"],
    "cl_past_due":           ["Past Due Claims"],
    "cl_high_risk":          ["High Risk Claims"],
    "cl_securities":         ["Lending Against Securities (Bonds & Shares)"],
    "cl_other":              ["Other Assets"],
    "cl_obs":                ["Off Balance Sheet Items"],
    # NPA
    "restructure":           ["Restructure Loan/Reschedule Loan"],
    "substandard":           ["Substandard Loan"],
    "doubtful":              ["Doubtful Loan"],
    "loss_loan":             ["Loss Loan"],
    "gross_npa_ratio":       ["Gross Npa To Gross Advances"],
    "net_npa_ratio":         ["Net Npa To Net Advances"],
    "llp_total":             ["Loan Loss Provision"],
    "interest_suspense":     ["Interest Suspense"],
    # Investment
    "held_trading":          ["Held For Trading"],
    "held_maturity":         ["Held To Maturity"],
    "avail_sale":            ["Available For Sale"],
    "total_investment":      ["Total Investment"],
}


@st.cache_data(show_spinner="Parsing Basel data...")
def load_data(uploaded):
    df = pd.read_excel(uploaded, sheet_name="Data")
    # Drop #REF! helper rows
    df = df[df["Helper"].astype(str) != "#REF!"].copy()
    df["Rs_parsed"] = df["Rs"].apply(parse_rs)
    df["Particulars"] = df["Particulars"].str.strip()

    periods = df["Month"].dropna().unique().tolist()
    rows = []
    for period in periods:
        sub = df[df["Month"] == period]
        row = {"Period": period}
        for key, names in METRIC_MAP.items():
            for name in names:
                hit = sub[sub["Particulars"] == name]
                if len(hit) > 0:
                    row[key] = hit.iloc[0]["Rs_parsed"]
                    break
            if key not in row:
                row[key] = np.nan
        rows.append(row)

    mdf = pd.DataFrame(rows)
    return mdf, df


# ================================================================
# 4. FORMATTING HELPERS
# ================================================================
def fmt_mn(v, d=1):
    if pd.isna(v): return "—"
    return f"NPR {v/1e3:,.{d}f} Mn"

def fmt_bn(v, d=2):
    if pd.isna(v): return "—"
    return f"NPR {v/1e6:,.{d}f} Bn"

def fmt_pct(v, d=2):
    if pd.isna(v): return "—"
    return f"{v:.{d}f}%"

def fmt_num(v, d=0):
    if pd.isna(v): return "—"
    return f"{v:,.{d}f}"

def delta_bps(curr, prev):
    if pd.isna(curr) or pd.isna(prev): return None
    return round((curr - prev) * 100)


def kpi_card_html(label, value, color, icon, sub="", bar_pct=0, bar_color=None):
    bc = bar_color or color
    return f"""<div class="kpi-card">
        <div class="kpi-glow" style="background:{color}"></div>
        <div class="kpi-icon" style="background:{color}18;color:{color}">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-val" style="color:{color}">{value}</div>
        {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
        {"<div class='kpi-bar'><div class='kpi-bar-fill' style='width:"+str(bar_pct)+"%;background:"+bc+"'></div></div>" if bar_pct else ""}
    </div>"""


# ================================================================
# 5. PLOTLY CHART HELPERS
# ================================================================
PLOTLY_KW = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", color=C["muted"], size=11),
    margin=dict(t=36, b=48, l=56, r=16),
)
AXIS_KW = dict(
    gridcolor="rgba(30,45,74,0.45)",
    zerolinecolor="rgba(30,45,74,0.45)",
    showline=False,
)
LEGEND_KW = dict(
    orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1,
    font=dict(size=11, color=C["muted"]),
)


def _line_trace(x, y, name, color, dash=None, width=2.5, fill=False):
    kw = dict(x=x, y=y, name=name, line=dict(color=color, width=width, dash=dash))
    if fill:
        kw["fill"] = "tozeroy"
        kw["fillcolor"] = color.replace(")", ",0.08)").replace("rgb", "rgba")
    return go.Scatter(**kw)


def _bar_trace(x, y, name, color, text=None):
    return go.Bar(x=x, y=y, name=name, marker_color=color,
                  text=text, textposition="outside",
                  textfont=dict(size=10, color=C["muted"]),
                  marker_line_width=0, hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>")


# ================================================================
# 6. CHART BUILDERS
# ================================================================

def chart_car_trend(mdf):
    """Capital Adequacy Ratio trend with NRB minimums."""
    fig = go.Figure()
    x = mdf["Period"]
    fig.add_trace(_line_trace(x, mdf["cet1_ratio"], "CET1 Ratio", C["green"], fill=True))
    fig.add_trace(_line_trace(x, mdf["total_car"],    "Total CAR",   C["cyan"],  fill=True))
    fig.add_trace(_line_trace(x, [NRB_CET1_MIN]*len(x),  "NRB CET1 Min (8%)",   C["red"],  dash="dash", width=1.2))
    fig.add_trace(_line_trace(x, [NRB_TOTAL_MIN]*len(x), "NRB Total Min (11%)", C["red"],  dash="dot",  width=1.2))
    fig.update_layout(
        **PLOTLY_KW, legend=LEGEND_KW,
        yaxis=dict(**AXIS_KW, ticksuffix="%", title="Ratio (%)"),
        xaxis=dict(**AXIS_KW, title=""),
        hovermode="x unified",
    )
    return fig


def chart_rwe_stacked(mdf):
    """RWE breakdown stacked bar over time."""
    comps = [
        ("rwe_credit",      "Credit Risk",      C["green"]),
        ("rwe_operational",  "Operational Risk", C["cyan"]),
        ("rwe_market",       "Market Risk",      C["amber"]),
        ("pillar2_adj",      "Pillar II Adj.",   C["purple"]),
        ("rwe_cap_charge",   "Capital Charge",   C["pink"]),
        ("risk_mgmt_adj",    "Risk Mgmt Adj.",   C["blue"]),
        ("nla_shortfall",    "NLA Shortfall",    C["red"]),
    ]
    fig = go.Figure()
    for key, name, color in comps:
        vals = mdf[key].fillna(0)
        if vals.abs().sum() > 0:
            fig.add_trace(go.Bar(
                x=mdf["Period"], y=vals, name=name,
                marker_color=color, marker_line_width=0,
                hovertemplate=f"{name}<br>%{{y:,.0f}}<extra></extra>"
            ))
    fig.update_layout(
        **PLOTLY_KW, legend=LEGEND_KW, barmode="stack",
        yaxis=dict(**AXIS_KW, title="RWE (NPR '000)"),
        xaxis=dict(**AXIS_KW, title=""),
        hovermode="x unified",
    )
    return fig


def chart_capital_composition(mdf):
    """Stacked bar: Tier 1 components + Tier 2 components over time."""
    fig = go.Figure()
    t1_parts = [
        ("paid_up_capital",    "Paid Up Capital",  C["green"]),
        ("share_premium",      "Share Premium",    C["cyan"]),
        ("statutory_reserves", "Statutory Reserves", C["blue"]),
        ("retained_earnings",  "Retained Earnings",  C["amber"]),
        ("cumulative_profit",  "Cumulative Profit",  C["purple"]),
        ("cap_adj_reserve",    "Cap. Adj. Reserve",  C["pink"]),
    ]
    t2_parts = [
        ("gen_llp",        "Gen. LLP",       C["cyan"]),
        ("exch_reserves",  "Exch. Reserves", C["amber"]),
        ("inv_adj_reserve","Inv. Adj. Res.", C["green"]),
        ("sub_debt",       "Sub. Debt",      C["blue"]),
    ]
    for key, name, color in t1_parts:
        vals = mdf[key].fillna(0)
        if vals.abs().sum() > 0:
            fig.add_trace(go.Bar(x=mdf["Period"], y=vals, name=f"T1: {name}",
                                 marker_color=color, marker_line_width=0))
    for key, name, color in t2_parts:
        vals = mdf[key].fillna(0)
        if vals.abs().sum() > 0:
            fig.add_trace(go.Bar(x=mdf["Period"], y=vals, name=f"T2: {name}",
                                 marker_color=color, marker_line_width=0,
                                 marker_pattern_shape="/"))
    fig.update_layout(
        **PLOTLY_KW, legend=LEGEND_KW, barmode="stack",
        yaxis=dict(**AXIS_KW, title="Capital (NPR '000)"),
        xaxis=dict(**AXIS_KW, title=""),
        hovermode="x unified",
    )
    return fig


def chart_capital_donut(row):
    """Donut chart for selected period's capital breakdown."""
    t1 = row.get("core_capital", np.nan)
    t2 = row.get("tier2_capital", np.nan)
    if pd.isna(t1): t1 = 0
    if pd.isna(t2): t2 = 0
    total = t1 + t2
    if total == 0: total = 1

    fig = go.Figure(go.Pie(
        values=[t1, t2],
        labels=["Tier 1 Capital", "Tier 2 Capital"],
        marker_colors=[C["green"], C["cyan"]],
        hole=0.72,
        textinfo="percent",
        textfont=dict(size=13, color=C["text"]),
        hovertemplate="<b>%{label}</b><br>NPR %{value:,.0f} ('000)<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_KW, margin=dict(t=10, b=10, l=10, r=10),
                      showlegend=True,
                      legend=dict(orientation="h", y=-0.05, font=dict(size=12, color=C["muted"])))
    return fig


def chart_credit_portfolio(row):
    """Horizontal bar of credit RWA by portfolio for one period."""
    items = [
        ("cl_retail",        "Regulatory Retail"),
        ("cl_corporate",     "Corporate & Securities"),
        ("cl_banks",         "Banks"),
        ("cl_residential",   "Residential Mortgage"),
        ("cl_high_risk",     "High Risk Claims"),
        ("cl_securities",    "Lending vs Securities"),
        ("cl_other",         "Other Assets"),
        ("cl_obs",           "Off-Balance Sheet"),
        ("cl_past_due",      "Past Due Claims"),
        ("cl_commercial_re", "Commercial Real Estate"),
        ("cl_govt",          "Government & Central Bank"),
    ]
    labels, vals, colors = [], [], []
    for key, name in items:
        v = row.get(key, np.nan)
        if pd.notna(v) and v != 0:
            labels.append(name)
            vals.append(v)
    # Color by magnitude
    mx = max(vals) if vals else 1
    color_seq = [C["green"], C["cyan"], C["blue"], C["amber"], C["purple"], C["pink"], C["red"]]
    colors = [color_seq[min(int(v/mx*5), len(color_seq)-1)] for v in vals]

    fig = go.Figure(go.Bar(
        x=vals, y=labels, orientation="h",
        marker_color=colors, marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>NPR %{x:,.0f} ('000)<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_KW, margin=dict(t=10, b=20, l=180, r=40),
        xaxis=dict(**AXIS_KW, title="RWE (NPR '000)"),
        yaxis=dict(**AXIS_KW, title="", autorange="reversed"),
        showlegend=False, height=max(320, len(labels)*36),
    )
    return fig


def chart_npa_stacked(mdf):
    """Stacked bar: NPA classification over time."""
    cats = [
        ("restructure",  "Restructured",  C["blue"]),
        ("substandard",  "Substandard",   C["amber"]),
        ("doubtful",     "Doubtful",      C["red"]),
        ("loss_loan",    "Loss",          C["pink"]),
    ]
    fig = go.Figure()
    for key, name, color in cats:
        vals = mdf[key].fillna(0)
        if vals.abs().sum() > 0:
            fig.add_trace(go.Bar(
                x=mdf["Period"], y=vals, name=name,
                marker_color=color, marker_line_width=0,
                hovertemplate=f"{name}<br>%{{y:,.0f}} ('000)<extra></extra>"
            ))
    fig.update_layout(
        **PLOTLY_KW, legend=LEGEND_KW, barmode="stack",
        yaxis=dict(**AXIS_KW, title="NPA (NPR '000)"),
        xaxis=dict(**AXIS_KW, title=""),
        hovermode="x unified",
    )
    return fig


def chart_npa_ratios(mdf):
    """Dual-line: Gross NPA and Net NPA ratios."""
    fig = go.Figure()
    fig.add_trace(_line_trace(mdf["Period"], mdf["gross_npa_ratio"],
                              "Gross NPA Ratio", C["red"], width=2.5))
    fig.add_trace(_line_trace(mdf["Period"], mdf["net_npa_ratio"],
                              "Net NPA Ratio", C["amber"], width=2.5))
    fig.update_layout(
        **PLOTLY_KW, legend=LEGEND_KW, hovermode="x unified",
        yaxis=dict(**AXIS_KW, ticksuffix="%", title="NPA Ratio (%)"),
        xaxis=dict(**AXIS_KW, title=""),
    )
    return fig


def chart_rwe_donut(row):
    """Donut of RWE components for selected period."""
    comps = [
        ("rwe_credit",     "Credit Risk",     C["green"]),
        ("rwe_operational", "Operational Risk", C["cyan"]),
        ("rwe_market",      "Market Risk",      C["amber"]),
        ("pillar2_adj",     "Pillar II",        C["purple"]),
        ("rwe_cap_charge",  "Capital Charge",   C["pink"]),
        ("risk_mgmt_adj",   "Risk Mgmt",        C["blue"]),
        ("nla_shortfall",   "NLA Shortfall",    C["red"]),
    ]
    labels, vals, colors = [], [], []
    for key, name, color in comps:
        v = row.get(key, np.nan)
        if pd.notna(v) and v != 0:
            labels.append(name)
            vals.append(v)
            colors.append(color)
    if not vals:
        return go.Figure()
    fig = go.Figure(go.Pie(
        values=vals, labels=labels, marker_colors=colors,
        hole=0.68, textinfo="percent",
        textfont=dict(size=11, color=C["text"]),
        hovertemplate="<b>%{label}</b><br>NPR %{value:,.0f} ('000)<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_KW, margin=dict(t=10, b=10, l=10, r=10),
                      showlegend=True,
                      legend=dict(orientation="h", y=-0.08, font=dict(size=10, color=C["muted"])))
    return fig


def chart_investment_trend(mdf):
    """Stacked area: Investment portfolio over time."""
    cats = [
        ("held_trading", "Held for Trading",  C["green"]),
        ("held_maturity", "Held to Maturity",  C["cyan"]),
        ("avail_sale",   "Available for Sale", C["amber"]),
    ]
    fig = go.Figure()
    for key, name, color in cats:
        vals = mdf[key].fillna(0)
        if vals.abs().sum() > 0:
            fig.add_trace(go.Scatter(
                x=mdf["Period"], y=vals, name=name,
                line=dict(color=color, width=1.5),
                fill="tozeroy",
                fillcolor=color.replace(")", ",0.12)").replace("#", "rgba(")
                    if color.startswith("#") else color,
                stackgroup="one",
                hovertemplate=f"{name}<br>%{{y:,.0f}} ('000)<extra></extra>",
            ))
    fig.update_layout(
        **PLOTLY_KW, legend=LEGEND_KW, hovermode="x unified",
        yaxis=dict(**AXIS_KW, title="Investment (NPR '000)"),
        xaxis=dict(**AXIS_KW, title=""),
    )
    return fig


# ================================================================
# 7. MAIN APPLICATION
# ================================================================
def main():
    inject_css()

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom:28px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                <div style="width:36px;height:36px;border-radius:10px;
                     background:linear-gradient(135deg,#10B981,#06B6D4);
                     display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:16px;">🏛️</span>
                </div>
                <div>
                    <div style="font-size:15px;font-weight:800;color:#E2E8F0;
                         letter-spacing:-0.3px;">BaselReport</div>
                    <div style="font-size:9px;color:#64748B;letter-spacing:1.5px;
                         text-transform:uppercase;">NRB Compliance Suite</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-head">Data Source</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload baseldata.xlsx",
            type=["xlsx"],
            label_visibility="collapsed",
            help="Upload the Basel III data Excel file",
        )

    # ── Load data ────────────────────────────────────────────────
    if not uploaded:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:60vh;gap:20px;">
            <div style="width:80px;height:80px;border-radius:20px;
                 background:linear-gradient(135deg,#10B98118,#06B6D418);
                 border:1px solid #1E2D4A;display:flex;align-items:center;
                 justify-content:center;font-size:32px;">📊</div>
            <div style="font-size:20px;font-weight:700;color:#E2E8F0;">
                Upload Basel Data</div>
            <div style="font-size:14px;color:#64748B;max-width:400px;text-align:center;">
                Select the <b>baseldata.xlsx</b> file from the sidebar to
                load your regulatory reporting data.
            </div>
        </div>""", unsafe_allow_html=True)
        return

    try:
        mdf, raw_df = load_data(uploaded)
    except Exception as e:
        st.error(f"Failed to parse Excel file: {e}")
        return

    if mdf.empty:
        st.warning("No valid data found in the file.")
        return

    n_periods = len(mdf)

    # ── Sidebar controls ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown('<div class="section-head">Period Filter</div>', unsafe_allow_html=True)
        sel_idx = st.selectbox(
            "Reporting Period",
            range(n_periods),
            format_func=lambda i: mdf.iloc[i]["Period"],
            index=n_periods - 1,
            label_visibility="collapsed",
        )
        sel_row = mdf.iloc[sel_idx]
        prev_row = mdf.iloc[sel_idx - 1] if sel_idx > 0 else None

        st.markdown("---")
        st.markdown('<div class="section-head">Quick Stats</div>', unsafe_allow_html=True)
        st.caption(f"Total periods: **{n_periods}**")
        st.caption(f"Date range: **{mdf.iloc[0]['Period']}** → **{mdf.iloc[-1]['Period']}**")
        st.caption(f"Data points parsed: **{len(METRIC_MAP)}** metrics × {n_periods} periods")

    # ── Computed values ──────────────────────────────────────────
    cet1   = sel_row.get("cet1_ratio", np.nan)
    tcar   = sel_row.get("total_car", np.nan)
    rwe    = sel_row.get("rwe_total", np.nan)
    gnpa   = sel_row.get("gross_npa_ratio", np.nan)
    nnpa   = sel_row.get("net_npa_ratio", np.nan)
    tcap   = sel_row.get("total_capital_fund", np.nan)
    core   = sel_row.get("core_capital", np.nan)
    tier2  = sel_row.get("tier2_capital", np.nan)

    cet1_d  = delta_bps(sel_row.get("cet1_ratio"), prev_row.get("cet1_ratio") if prev_row is not None else None)
    tcar_d  = delta_bps(sel_row.get("total_car"), prev_row.get("total_car") if prev_row is not None else None)
    gnpa_d  = delta_bps(sel_row.get("gross_npa_ratio"), prev_row.get("gross_npa_ratio") if prev_row is not None else None)

    cet1_ok = not pd.isna(cet1) and cet1 >= NRB_CET1_MIN
    tcar_ok = not pd.isna(tcar) and tcar >= NRB_TOTAL_MIN

    # ── Header Banner ────────────────────────────────────────────
    if cet1_ok and tcar_ok:
        banner_color = f"{C['green']}18"
        banner_border = f"{C['green']}30"
        banner_text = C["green"]
        banner_msg = "All capital ratios above NRB minimum requirements"
        banner_icon = "✓"
    else:
        banner_color = f"{C['red']}18"
        banner_border = f"{C['red']}30"
        banner_text = C["red"]
        banner_msg = "Capital ratios below NRB minimum — action required"
        banner_icon = "⚠"

    st.markdown(f"""
    <div class="status-banner" style="background:{banner_color};
         border:1px solid {banner_border};color:{banner_text};">
        <div class="status-dot" style="background:{banner_text};color:{banner_text};"></div>
        <span>{banner_msg}</span>
        <span style="margin-left:auto;font-size:11px;color:{C['muted']};">
            {sel_row['Period']} | {n_periods} periods loaded
        </span>
    </div>""", unsafe_allow_html=True)

    # ── KPI Cards ────────────────────────────────────────────────
    def d_str(d):
        if d is None: return ""
        sign = "▲" if d >= 0 else "▼"
        col = C["green"] if d >= 0 else C["red"]
        return f'<span style="color:{col}">{sign} {abs(d)} bps</span>'

    kpi_html = f"""<div class="kpi-grid">
    {kpi_card_html("CET1 Ratio", fmt_pct(cet1), C["green"], "🛡️",
                   d_str(cet1_d),
                   min(cet1/20*100, 100) if not pd.isna(cet1) else 0)}
    {kpi_card_html("Total CAR", fmt_pct(tcar), C["cyan"], "🏦",
                   d_str(tcar_d),
                   min(tcar/20*100, 100) if not pd.isna(tcar) else 0)}
    {kpi_card_html("Total RWE", fmt_bn(rwe), C["amber"], "📊",
                   fmt_mn(rwe) if not pd.isna(rwe) else "",
                   80)}
    {kpi_card_html("Gross NPA", fmt_pct(gnpa), C["red"], "⚠️",
                   d_str(gnpa_d),
                   min(gnpa/5*100, 100) if not pd.isna(gnpa) else 0)}
    {kpi_card_html("Net NPA", fmt_pct(nnpa), C["purple"], "📉",
                   "", 60, C["purple"])}
    </div>"""
    st.markdown(kpi_html, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈  Overview", "💰  Capital", "⚡  Risk Analysis",
        "🔴  Asset Quality", "📋  Data Table"
    ])

    # ────── TAB 1: OVERVIEW ─────────────────────────────────────
    with tab1:
        col_l, col_r = st.columns([3, 2], gap="16px")
        with col_l:
            st.markdown('<div class="section-head">Capital Adequacy Trend</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_car_trend(mdf), use_container_width=True)
        with col_r:
            st.markdown('<div class="section-head">Capital Structure</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_capital_donut(sel_row), use_container_width=True)

        st.markdown('<div class="section-head">RWE Evolution</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_rwe_stacked(mdf), use_container_width=True)

        # Mini metrics row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Core Capital", fmt_mn(core),
                      delta=fmt_mn(core - prev_row["core_capital"]) if prev_row is not None and pd.notna(core) and pd.notna(prev_row["core_capital"]) else None,
                      delta_color="normal")
        with c2:
            st.metric("Tier 2 Capital", fmt_mn(tier2),
                      delta=fmt_mn(tier2 - prev_row["tier2_capital"]) if prev_row is not None and pd.notna(tier2) and pd.notna(prev_row["tier2_capital"]) else None,
                      delta_color="normal")
        with c3:
            st.metric("Total Capital Fund", fmt_mn(tcap),
                      delta=fmt_mn(tcap - prev_row["total_capital_fund"]) if prev_row is not None and pd.notna(tcap) and pd.notna(prev_row["total_capital_fund"]) else None,
                      delta_color="normal")
        with c4:
            st.metric("Total Investment", fmt_mn(sel_row.get("total_investment")),
                      delta=fmt_mn(sel_row.get("total_investment", 0) - (prev_row.get("total_investment", 0) if prev_row is not None else 0)),
                      delta_color="normal")

    # ────── TAB 2: CAPITAL ──────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-head">Capital Composition Over Time</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_capital_composition(mdf), use_container_width=True)

        col_l, col_r = st.columns(2, gap="16px")
        with col_l:
            st.markdown('<div class="section-head">Tier 1 vs Tier 2 Breakdown</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_capital_donut(sel_row), use_container_width=True)
        with col_r:
            st.markdown('<div class="section-head">Capital Components Detail</div>',
                        unsafe_allow_html=True)
            comp_data = {
                "Component": [
                    "Paid Up Capital", "Share Premium", "Statutory Reserves",
                    "Retained Earnings", "Cumulative Profit", "Cap. Adj. Reserve",
                    "— Tier 1 Subtotal —", "",
                    "Gen. Loan Loss Prov.", "Exchange Reserves", "Inv. Adj. Reserve",
                    "Subordinated Debt",
                    "— Tier 2 Subtotal —", "",
                    "Total Capital Fund"
                ],
                "Amount (NPR '000)": [
                    sel_row.get("paid_up_capital"), sel_row.get("share_premium"),
                    sel_row.get("statutory_reserves"), sel_row.get("retained_earnings"),
                    sel_row.get("cumulative_profit"), sel_row.get("cap_adj_reserve"),
                    sel_row.get("core_capital"), None,
                    sel_row.get("gen_llp"), sel_row.get("exch_reserves"),
                    sel_row.get("inv_adj_reserve"), sel_row.get("sub_debt"),
                    sel_row.get("tier2_capital"), None,
                    sel_row.get("total_capital_fund"),
                ],
            }
            cdf = pd.DataFrame(comp_data)
            st.dataframe(cdf, use_container_width=True, hide_index=True,
                         column_config={"Amount (NPR '000)": st.column_config.NumberColumn(format="%,.0f")})

        st.markdown('<div class="section-head">Investment Portfolio Trend</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_investment_trend(mdf), use_container_width=True)

    # ────── TAB 3: RISK ANALYSIS ───────────────────────────────
    with tab3:
        col_l, col_r = st.columns([3, 2], gap="16px")
        with col_l:
            st.markdown('<div class="section-head">Credit RWA by Portfolio</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_credit_portfolio(sel_row), use_container_width=True)
        with col_r:
            st.markdown('<div class="section-head">RWE Composition</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_rwe_donut(sel_row), use_container_width=True)

        st.markdown('<div class="section-head">RWE Components Over Time</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_rwe_stacked(mdf), use_container_width=True)

        # RWE detail table for selected period
        st.markdown('<div class="section-head">RWE Detail — ' + sel_row["Period"] + '</div>',
                    unsafe_allow_html=True)
        rwe_detail = {
            "Component": [
                "Credit Risk RWE", "Operational Risk RWE", "Market Risk RWE",
                "Pillar II Adjustments", "Capital Charge RWE",
                "Risk Mgmt Adjustment", "NLA Shortfall",
                "Total RWE"
            ],
            "Amount (NPR '000)": [
                sel_row.get("rwe_credit"), sel_row.get("rwe_operational"),
                sel_row.get("rwe_market"), sel_row.get("pillar2_adj"),
                sel_row.get("rwe_cap_charge"), sel_row.get("risk_mgmt_adj"),
                sel_row.get("nla_shortfall"), sel_row.get("rwe_total"),
            ],
        }
        rdf = pd.DataFrame(rwe_detail)
        st.dataframe(rdf, use_container_width=True, hide_index=True,
                     column_config={"Amount (NPR '000)": st.column_config.NumberColumn(format="%,.0f")})

    # ────── TAB 4: ASSET QUALITY ────────────────────────────────
    with tab4:
        col_l, col_r = st.columns(2, gap="16px")
        with col_l:
            st.markdown('<div class="section-head">NPA Classification Trend</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_npa_stacked(mdf), use_container_width=True)
        with col_r:
            st.markdown('<div class="section-head">NPA Ratio Trends</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_npa_ratios(mdf), use_container_width=True)

        # NPA detail
        st.markdown('<div class="section-head">Asset Quality Detail — ' + sel_row["Period"] + '</div>',
                    unsafe_allow_html=True)
        npa_detail = {
            "Metric": [
                "Restructured Loans", "Substandard Loans", "Doubtful Loans",
                "Loss Loans", "Total Classified",
                "Gross NPA Ratio", "Net NPA Ratio",
                "Loan Loss Provision", "Interest Suspense",
            ],
            "Value": [
                sel_row.get("restructure"), sel_row.get("substandard"),
                sel_row.get("doubtful"), sel_row.get("loss_loan"),
                (sel_row.get("restructure",0) or 0) + (sel_row.get("substandard",0) or 0)
                + (sel_row.get("doubtful",0) or 0) + (sel_row.get("loss_loan",0) or 0),
                sel_row.get("gross_npa_ratio"), sel_row.get("net_npa_ratio"),
                sel_row.get("llp_total"), sel_row.get("interest_suspense"),
            ],
            "Unit": ["NPR '000"]*5 + ["%","%"] + ["NPR '000"]*2,
        }
        ndf = pd.DataFrame(npa_detail)
        st.dataframe(ndf, use_container_width=True, hide_index=True)

        # Provision coverage ratio
        total_npa = ((sel_row.get("substandard",0) or 0) +
                     (sel_row.get("doubtful",0) or 0) +
                     (sel_row.get("loss_loan",0) or 0))
        llp = sel_row.get("llp_total", 0) or 0
        pcr = (llp / total_npa * 100) if total_npa > 0 else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Provision Coverage Ratio", f"{pcr:.1f}%")
        with c2:
            st.metric("Total Classified Loans", fmt_mn(total_npa))
        with c3:
            st.metric("Interest Suspense", fmt_mn(sel_row.get("interest_suspense")))

    # ────── TAB 5: DATA TABLE ───────────────────────────────────
    with tab5:
        st.markdown('<div class="section-head">Parsed Metrics Summary</div>',
                    unsafe_allow_html=True)
        st.caption("All extracted Basel III metrics across reporting periods. "
                   "Values are in NPR '000 unless marked as %.")

        # Transpose: metrics as rows, periods as columns
        display_cols = ["Period"]
        display_metrics = [
            ("cet1_ratio",          "CET1 Ratio (%)"),
            ("total_car",           "Total CAR (%)"),
            ("core_capital",        "Core Capital"),
            ("tier2_capital",       "Tier 2 Capital"),
            ("total_capital_fund",  "Total Capital Fund"),
            ("rwe_credit",          "RWE - Credit Risk"),
            ("rwe_operational",     "RWE - Operational Risk"),
            ("rwe_market",          "RWE - Market Risk"),
            ("rwe_total",           "Total RWE"),
            ("gross_npa_ratio",     "Gross NPA Ratio (%)"),
            ("net_npa_ratio",       "Net NPA Ratio (%)"),
            ("substandard",         "Substandard Loans"),
            ("doubtful",            "Doubtful Loans"),
            ("loss_loan",           "Loss Loans"),
            ("llp_total",           "Loan Loss Provision"),
            ("total_investment",    "Total Investment"),
            ("cl_retail",           "Claims - Retail"),
            ("cl_corporate",        "Claims - Corporate"),
            ("cl_banks",            "Claims - Banks"),
            ("cl_high_risk",        "High Risk Claims"),
        ]

        tdf = mdf[["Period"]].copy()
        for key, label in display_metrics:
            if key in mdf.columns:
                tdf[label] = mdf[key]

        # Format ratio columns as percentage
        pct_cols = [l for k, l in display_metrics if k in RATIO_KEYS and l in tdf.columns]
        for col in pct_cols:
            tdf[col] = tdf[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")

        # Format numeric columns
        num_cols = [c for c in tdf.columns if c != "Period" and c not in pct_cols]
        col_cfg = {"Period": st.column_config.TextColumn("Period")}
        for col in num_cols:
            col_cfg[col] = st.column_config.NumberColumn(
                col, format="%,.0f"
            )
        for col in pct_cols:
            col_cfg[col] = st.column_config.TextColumn(col)

        st.dataframe(tdf, use_container_width=True, hide_index=True,
                     column_config=col_cfg, height=500)

        # Raw data toggle
        with st.expander("Show Raw Excel Data", expanded=False):
            st.dataframe(raw_df[["Month", "Helper", "Particulars", "Rs"]],
                         use_container_width=True, hide_index=True, height=400)


# ================================================================
# 8. ENTRY POINT
# ================================================================
if __name__ == "__main__":
    main()
