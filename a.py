import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
import requests
import numpy as np

# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="Executive MIS | Basel Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Custom CSS (Dark Glassmorphism Theme) ----------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #3B82F6;
        --primary-light: #60A5FA;
        --secondary: #10B981;
        --danger: #EF4444;
        --warning: #F59E0B;
        --bg-dark: #0F172A;
        --bg-secondary: #1E293B;
        --card-bg: rgba(30, 41, 59, 0.6);
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --border: rgba(148, 163, 184, 0.2);
    }

    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at 80% -20%, rgba(59, 130, 246, 0.15) 0%, rgba(15, 23, 42, 0) 50%),
                    radial-gradient(circle at 0% 100%, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0) 50%),
                    #0F172A;
        color: var(--text-primary);
    }

    /* Header */
    .header-container {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(30, 41, 59, 0.4) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border);
        padding: 2rem 2.5rem; 
        border-radius: 24px; 
        margin-bottom: 2rem; 
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
    }
    .header-title { font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; background: linear-gradient(90deg, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .header-subtitle { opacity: 0.8; font-size: 1rem; margin-top: 0.5rem; color: var(--text-secondary); }
    .header-meta { display: flex; gap: 2rem; margin-top: 1.5rem; font-size: 0.9rem; color: var(--text-secondary); }
    .header-meta strong { color: var(--text-primary); font-weight: 600; }

    /* KPI Cards */
    .kpi-card {
        background: var(--card-bg); 
        backdrop-filter: blur(8px);
        border-radius: 16px; 
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: var(--primary);
        opacity: 0.8;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: var(--primary);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .kpi-label { font-size: 0.75rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 2rem; font-weight: 800; color: var(--text-primary); line-height: 1.1; }
    .kpi-delta { font-size: 0.85rem; font-weight: 600; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.25rem; }
    .kpi-delta.positive { color: var(--secondary); }
    .kpi-delta.negative { color: var(--danger); }
    .kpi-delta.neutral  { color: var(--text-secondary); }

    /* Status Badges */
    .status-badge { display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 600; margin-top: 1rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .status-badge.safe    { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .status-badge.warning { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .status-badge.danger  { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Section Headers */
    .section-header { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 2rem 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; }
    .section-header::before { content: ""; display: block; width: 4px; height: 24px; background: var(--primary); border-radius: 4px; }

    /* Streamlit Native Elements Overrrides */
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; background: var(--bg-secondary); padding: 0.5rem; border-radius: 12px; border: 1px solid var(--border); }
    .stTabs [data-baseweb="tab"] { padding: 0.5rem 1rem; border-radius: 8px; color: var(--text-secondary); font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: var(--primary) !important; color: white !important; }

    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0B1120 0%, #0F172A 100%) !important; 
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
    .sidebar-title { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #64748B; margin-bottom: 0.75rem; margin-top: 1rem; }
    
    div[data-testid="stMetric"] {
        background: var(--card-bg); 
        backdrop-filter: blur(8px);
        padding: 1rem; border-radius: 12px; 
        border: 1px solid var(--border);
    }
    div[data-testid="stMetric"] label { color: var(--text-secondary) !important; font-size: 0.8rem !important; }
    div[data-testid="stMetric"] div { color: var(--text-primary) !important; }

    .alert-box { padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; backdrop-filter: blur(8px); border: 1px solid; }
    .alert-box.success { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); color: #34D399; }
    .alert-box.warning { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); color: #FBBF24; }
    .alert-box.danger  { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: #F87171; }
    .alert-box.info    { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); color: #60A5FA; }

    /* Table styling */
    .stDataFrame { background: var(--bg-secondary) !important; border-radius: 12px; border: 1px solid var(--border); overflow: hidden; }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Loading ----------------------
@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        df = xls.parse("Data")

        df.columns = (
            df.columns.str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.replace('\xa0', ' ')
        )

        drop_cols = [c for c in df.columns if c.startswith("Unnamed")
                     or c in ("Helper", "Rs.1", "Rs.2", "Movements(%)")]
        df.drop(columns=drop_cols, errors="ignore", inplace=True)

        df["Month"]       = df["Month"].astype(str).str.strip()
        df["Particulars"] = df["Particulars"].astype(str).str.strip()

        # Coerce numeric
        df["Rs"] = pd.to_numeric(df["Rs"], errors="coerce")
        return df
    except Exception:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Failed to load data. Please check your connection and try again.")
    st.stop()

# ---------------------- Row-based Lookup Utility ----------------------
def find_particular(df: pd.DataFrame, keywords: list) -> str | None:
    for val in df["Particulars"].dropna().unique():
        val_lower = str(val).lower()
        if all(kw.lower() in val_lower for kw in keywords):
            return val
    return None

LABEL_GROSS_NPA  = find_particular(df, ["gross", "npa"])
LABEL_NET_NPA    = find_particular(df, ["net",   "npa"])
LABEL_CORE_CAP   = find_particular(df, ["core",  "capital"])
LABEL_TOTAL_CAP  = find_particular(df, ["total", "capital"])

labels_check = {
    "Gross NPA":     LABEL_GROSS_NPA,
    "Net NPA":       LABEL_NET_NPA,
    "Core Capital":  LABEL_CORE_CAP,
    "Total Capital": LABEL_TOTAL_CAP,
}

unresolved = [k for k, v in labels_check.items() if v is None]
if unresolved:
    st.error(f"⚠️ Could not find row labels for: **{', '.join(unresolved)}**")
    st.stop()

# ---------------------- Helper Functions ----------------------
def get_value(particular_label: str, month: str) -> float:
    mask = (df["Particulars"] == particular_label) & (df["Month"] == month)
    result = df.loc[mask, "Rs"]
    if result.empty:
        return 0.0
    val = result.iloc[0]
    return float(val) if pd.notna(val) else 0.0

def get_series(particular_label: str) -> pd.DataFrame:
    s = df[df["Particulars"] == particular_label][["Month", "Rs"]].copy()
    s = s.dropna(subset=["Rs"])
    return s.reset_index(drop=True)

def get_prev_month(month: str) -> str:
    months = df["Month"].dropna().unique().tolist()
    idx = months.index(month) if month in months else 0
    return months[max(0, idx - 1)]

def is_ratio_value(val: float) -> bool:
    return abs(val) <= 2.0

def format_value(val: float) -> str:
    if pd.isna(val): return "N/A"
    if is_ratio_value(val): return f"{val:.2%}"
    return f"{val:,.2f}"

def safe_pct_change(current: float, prev: float) -> float | None:
    if prev is None or abs(prev) < 1e-9: return None
    return ((current - prev) / abs(prev)) * 100.0

def get_status(val: float, threshold: float, lower_better: bool = True) -> str:
    if lower_better:
        if val <= threshold:          return "safe"
        elif val <= threshold * 1.2:  return "warning"
        return "danger"
    else:
        if val >= threshold:          return "safe"
        elif val >= threshold * 0.8:  return "warning"
        return "danger"

def draw_gauge(value: float, max_value: float, title: str, threshold: float,
               lower_better: bool = True, height: int = 220) -> go.Figure:
    v = value * 100 if is_ratio_value(value) else value
    t = threshold * 100 if is_ratio_value(threshold) else threshold
    m = max_value * 100 if is_ratio_value(max_value) else max_value

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=v,
        delta={"reference": t, "increasing": {"color": "#EF4444"}, "decreasing": {"color": "#10B981"}},
        gauge={
            "axis": {"range": [0, m * 1.5], "tickcolor": "#64748B", "gridcolor": "#334155"},
            "bar": {"color": "#3B82F6"},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 1,
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, t * 0.7], "color": "rgba(16, 185, 129, 0.2)"},
                {"range": [t * 0.7, t], "color": "rgba(245, 158, 11, 0.2)"},
                {"range": [t, m], "color": "rgba(239, 68, 68, 0.2)"}
            ],
            "threshold": {"line": {"color": "#F87171", "width": 4}, "value": t}
        },
        number={"suffix": "%", "font": {"size": 28, "color": "#F8FAFC"}},
        title={"text": title, "font": {"size": 14, "color": "#94A3B8"}}
    ))
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# ---------------------- Sidebar Controls ----------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: left; padding: 1.5rem 0; margin-bottom: 1rem;">
            <h2 style="margin: 0; font-size: 1.4rem; color: #F8FAFC; font-weight: 800;">📊 Basel Analytics</h2>
            <p style="opacity: 0.6; margin: 0.5rem 0 0 0; font-size: 0.85rem;">Executive MIS Suite</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">📊 Report Controls</div>', unsafe_allow_html=True)
    all_months = df["Month"].dropna().unique().tolist()
    selected_month = st.selectbox("Reporting Period", options=all_months, index=len(all_months) - 1)
    prev_month = get_prev_month(selected_month)

    available_parts = df["Particulars"].dropna().unique().tolist()
    selected_parts = st.multiselect(
        "Select Metrics", options=available_parts,
        default=available_parts[:3] if len(available_parts) >= 3 else available_parts
    )

    st.markdown('<div class="sidebar-title">🎛️ Analysis Options</div>', unsafe_allow_html=True)
    show_table = st.checkbox("Show Data Tables", value=True)
    show_raw = st.checkbox("Show Raw Data", value=False)
    comparison_periods = st.slider("Compare Last N Periods", 1, 6, 3)

    st.markdown('<div class="sidebar-title">⚠️ Compliance Thresholds</div>', unsafe_allow_html=True)
    npa_threshold = st.number_input("NPA Warning (%)", value=5.0, step=0.5) / 100
    cap_threshold = st.number_input("Capital Floor (%)", value=8.5, step=0.5) / 100

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">ℹ️ System</div>', unsafe_allow_html=True)
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption(f"Total Records: {len(df):,}")
    st.caption(f"Periods: {len(all_months)}")

# ---------------------- KPI Values ----------------------
kpi = {
    "gross_npa_c":  get_value(LABEL_GROSS_NPA,  selected_month),
    "gross_npa_p":  get_value(LABEL_GROSS_NPA,  prev_month),
    "net_npa_c":    get_value(LABEL_NET_NPA,    selected_month),
    "net_npa_p":    get_value(LABEL_NET_NPA,    prev_month),
    "core_cap_c":   get_value(LABEL_CORE_CAP,   selected_month),
    "core_cap_p":   get_value(LABEL_CORE_CAP,   prev_month),
    "total_cap_c":  get_value(LABEL_TOTAL_CAP,  selected_month),
    "total_cap_p":  get_value(LABEL_TOTAL_CAP,  prev_month),
}

# ---------------------- Header ----------------------
st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">Executive MIS Dashboard</h1>
        <p class="header-subtitle">Financial Risk Intelligence Platform | Basel III Compliance Monitoring</p>
        <div class="header-meta">
            <span>📅 Current Period: <strong>{selected_month}</strong></span>
            <span>📆 Prior Period: <strong>{prev_month}</strong></span>
            <span>📈 Data Points: <strong>{len(df):,}</strong></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------- KPI Cards Row ----------------------
def create_kpi_card(label, current, prev, lower_better=True, threshold=None):
    delta = current - prev
    improving = (delta < 0 and lower_better) or (delta > 0 and not lower_better)
    is_zero_delta = abs(delta) < 1e-9

    if is_zero_delta:
        color_class = "neutral"
        arrow = "→"
        delta_text = "No change"
    else:
        color_class = "positive" if improving else "negative"
        arrow = "↑" if delta > 0 else "↓"
        pct = safe_pct_change(current, prev)
        if pct is None:
            delta_text = f"{format_value(abs(delta))} (abs.)"
        else:
            display_pct = pct if abs(pct) < 1e6 else 1e6 * np.sign(pct)
            delta_text = f"{abs(display_pct):,.2f}%"

    status = ""
    if threshold is not None:
        status_class = get_status(current, threshold, lower_better)
        status_text = ("✓ Safe" if status_class == "safe"
                       else ("⚠ Warning" if status_class == "warning" else "✗ Alert"))
        status = f'<span class="status-badge {status_class}">{status_text}</span>'

    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{format_value(current)}</div>
        <div class="kpi-delta {color_class}">
            {arrow} {delta_text} vs prior
        </div>
        {status}
    </div>
    """

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(create_kpi_card("Gross NPA", kpi["gross_npa_c"], kpi["gross_npa_p"], lower_better=True, threshold=npa_threshold), unsafe_allow_html=True)
with col2:
    st.markdown(create_kpi_card("Net NPA", kpi["net_npa_c"], kpi["net_npa_p"], lower_better=True, threshold=npa_threshold), unsafe_allow_html=True)
with col3:
    st.markdown(create_kpi_card("Core Capital", kpi["core_cap_c"], kpi["core_cap_p"], lower_better=False, threshold=0.055), unsafe_allow_html=True)
with col4:
    st.markdown(create_kpi_card("Capital Adequacy", kpi["total_cap_c"], kpi["total_cap_p"], lower_better=False, threshold=cap_threshold), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------- Alert Banner ----------------------
if kpi["gross_npa_c"] > npa_threshold:
    st.markdown(f"""
        <div class="alert-box danger">
            <span style="font-size: 1.5rem;">🚨</span>
            <div>
                <strong>Gross NPA Alert:</strong> Current ratio ({kpi['gross_npa_c']:.2%}) exceeds threshold ({npa_threshold:.1%})
            </div>
        </div>
    """, unsafe_allow_html=True)
elif kpi["gross_npa_c"] > npa_threshold * 0.8:
    st.markdown(f"""
        <div class="alert-box warning">
            <span style="font-size: 1.5rem;">⚠️</span>
            <div>
                <strong>NPA Warning:</strong> Gross NPA ({kpi['gross_npa_c']:.2%}) approaching threshold
            </div>
        </div>
    """, unsafe_allow_html=True)

if kpi["total_cap_c"] < cap_threshold:
    st.markdown(f"""
        <div class="alert-box danger">
            <span style="font-size: 1.5rem;">🚨</span>
            <div>
                <strong>Capital Alert:</strong> Total Capital ({kpi['total_cap_c']:.2%}) below regulatory floor ({cap_threshold:.1%})
            </div>
        </div>
    """, unsafe_allow_html=True)
elif kpi["total_cap_c"] < cap_threshold * 1.2:
    st.markdown(f"""
        <div class="alert-box warning">
            <span style="font-size: 1.5rem;">⚠️</span>
            <div>
                <strong>Capital Buffer Warning:</strong> Adequacy ratio ({kpi['total_cap_c']:.2%}) near regulatory minimum
            </div>
        </div>
    """, unsafe_allow_html=True)

# Plotly global theme settings
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
    margin=dict(l=20, r=20, t=40, b=40)
)

# ---------------------- Main Tabs ----------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Performance Overview",
    "📉 Asset Quality",
    "🛡️ Capital Compliance",
    "📋 Data Explorer"
])

# ── Tab 1: Performance Overview ───────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Multi-Metric Performance Trend</div>', unsafe_allow_html=True)

    if not selected_parts:
        st.warning("Please select metrics from the sidebar control panel.")
    else:
        trend_df = df[df["Particulars"].isin(selected_parts)].copy()
        fig1 = px.line(
            trend_df, x="Month", y="Rs", color="Particulars",
            markers=True, color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig1.update_traces(mode="lines+markers", marker=dict(size=8, line=dict(width=1, color="#0F172A")), line=dict(width=3))
        fig1.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", bgcolor="rgba(0,0,0,0)"),
            xaxis_title="Reporting Period", yaxis_title="Value (₹)",
            height=400, **PLOTLY_LAYOUT
        )
        fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
        fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown('<div class="section-header">Period-over-Period Comparison</div>', unsafe_allow_html=True)

    npa_gross_series = get_series(LABEL_GROSS_NPA)
    npa_net_series   = get_series(LABEL_NET_NPA)

    fig_comp = make_subplots(rows=1, cols=2, subplot_titles=("Gross NPA Trend", "Net NPA Trend"), horizontal_spacing=0.15)
    fig_comp.add_trace(
        go.Scatter(x=npa_gross_series["Month"], y=npa_gross_series["Rs"], name="Gross NPA", fill="tozeroy", line=dict(color="#3B82F6", width=2), fillcolor="rgba(59, 130, 246, 0.1)"), 
        row=1, col=1
    )
    fig_comp.add_trace(
        go.Scatter(x=npa_net_series["Month"], y=npa_net_series["Rs"], name="Net NPA", fill="tozeroy", line=dict(color="#10B981", width=2), fillcolor="rgba(16, 185, 129, 0.1)"), 
        row=1, col=2
    )
    fig_comp.add_hline(y=npa_threshold, line_dash="dash", line_color="#EF4444", annotation_text=f"Threshold ({npa_threshold:.1%})", row=1, col=1)
    fig_comp.add_hline(y=npa_threshold, line_dash="dash", line_color="#EF4444", annotation_text=f"Threshold ({npa_threshold:.1%})", row=1, col=2)
    fig_comp.update_layout(height=350, showlegend=False, **PLOTLY_LAYOUT)
    fig_comp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    fig_comp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    st.plotly_chart(fig_comp, use_container_width=True)

    if show_table:
        st.markdown('<div class="section-header">Key Metrics Summary</div>', unsafe_allow_html=True)
        summary_data = []
        for label, db_label in [("Gross NPA", LABEL_GROSS_NPA), ("Net NPA", LABEL_NET_NPA), ("Core Capital", LABEL_CORE_CAP), ("Total Capital", LABEL_TOTAL_CAP)]:
            series = get_series(db_label)
            if len(series) >= 2:
                cur, prv = series["Rs"].iloc[-1], series["Rs"].iloc[-2]
                pct = safe_pct_change(cur, prv)
                change_str = f"{pct:.2f}%" if pct is not None else "N/A (prev=0)"
            elif len(series) == 1:
                cur, prv, change_str = series["Rs"].iloc[-1], None, "N/A"
            else:
                continue

            summary_data.append({
                "Metric": label,
                "Current": format_value(cur),
                "Previous": format_value(prv) if prv is not None else "N/A",
                "Change": change_str,
                "Min": format_value(series["Rs"].min()),
                "Max": format_value(series["Rs"].max()),
                "Average": format_value(series["Rs"].mean())
            })

        if summary_data:
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

# ── Tab 2: Asset Quality ──────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Asset Quality Monitoring Dashboard</div>', unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(draw_gauge(kpi["gross_npa_c"], 0.15, "Gross NPA Ratio", npa_threshold, lower_better=True), use_container_width=True)
    with g2:
        st.plotly_chart(draw_gauge(kpi["net_npa_c"], 0.10, "Net NPA Ratio", npa_threshold * 0.8, lower_better=True), use_container_width=True)

    with st.expander("📚 NPA Classification Standards (Basel III)"):
        st.markdown("""
        | Category | Definition | Provisioning Rate |
        |----------|------------|-------------------|
        | **Standard** | Performing assets with timely repayment | 0.25% - 2.00% |
        | **Sub-Standard** | NPA for a period exceeding 90 days | 15% - 25% |
        | **Doubtful** | NPA for a period exceeding 12 months | 25% - 100% |
        | **Loss Asset** | Identified as non-recoverable | 100% |
        """)

    st.markdown('<div class="section-header">NPA Trend Analysis</div>', unsafe_allow_html=True)
    fig_npa = go.Figure()
    fig_npa.add_trace(go.Bar(
        x=npa_gross_series["Month"], y=npa_gross_series["Rs"], name="Gross NPA", marker_color="#3B82F6",
        text=npa_gross_series["Rs"].apply(format_value), textposition="outside", textfont=dict(color="#F8FAFC")
    ))
    fig_npa.add_trace(go.Scatter(
        x=npa_net_series["Month"], y=npa_net_series["Rs"], name="Net NPA", mode="lines+markers+text",
        line=dict(color="#EF4444", width=3), marker=dict(size=10),
        text=npa_net_series["Rs"].apply(format_value), textposition="top center", textfont=dict(color="#F8FAFC")
    ))
    fig_npa.update_layout(
        xaxis_title="Reporting Period", yaxis_title="NPA Ratio", hovermode="x unified",
        legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)"), height=400, barmode="group", **PLOTLY_LAYOUT
    )
    fig_npa.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    fig_npa.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    st.plotly_chart(fig_npa, use_container_width=True)

    if show_table:
        npa_combined = npa_gross_series.merge(npa_net_series, on="Month", suffixes=("_Gross", "_Net"))
        npa_combined.columns = ["Month", "Gross NPA", "Net NPA"]
        npa_combined["Spread"] = npa_combined["Gross NPA"] - npa_combined["Net NPA"]
        st.markdown('<div class="section-header">NPA Data Summary</div>', unsafe_allow_html=True)
        st.dataframe(npa_combined, use_container_width=True, hide_index=True)

# ── Tab 3: Capital Compliance ─────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Capital Adequacy & Compliance Analysis</div>', unsafe_allow_html=True)

    core_cap_series  = get_series(LABEL_CORE_CAP)
    total_cap_series = get_series(LABEL_TOTAL_CAP)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(draw_gauge(kpi["core_cap_c"], 0.15, "Core Capital Ratio", 0.055, lower_better=False), use_container_width=True)
    with g2:
        st.plotly_chart(draw_gauge(kpi["total_cap_c"], 0.20, "Total Capital Ratio", cap_threshold, lower_better=False), use_container_width=True)
    with g3:
        buffer = kpi["total_cap_c"] - cap_threshold
        st.plotly_chart(draw_gauge(abs(buffer), cap_threshold * 0.5, "Capital Buffer", cap_threshold * 0.1, lower_better=False), use_container_width=True)

    st.markdown('<div class="section-header">Capital Position Over Time</div>', unsafe_allow_html=True)
    cap_df = core_cap_series.merge(total_cap_series, on="Month", suffixes=("_Core", "_Total"))
    cap_df.columns = ["Month", "Core Capital", "Total Capital"]

    fig_cap = go.Figure()
    fig_cap.add_trace(go.Scatter(
        x=cap_df["Month"], y=cap_df["Core Capital"], name="Core Capital (Tier I)", fill="tozeroy", mode="lines+markers",
        line=dict(color="#60A5FA", width=3), fillcolor="rgba(96, 165, 250, 0.2)", marker=dict(size=8)
    ))
    fig_cap.add_trace(go.Scatter(
        x=cap_df["Month"], y=cap_df["Total Capital"], name="Total Capital", fill="tonexty", mode="lines+markers",
        line=dict(color="#3B82F6", width=3), fillcolor="rgba(59, 130, 246, 0.2)", marker=dict(size=8)
    ))
    fig_cap.add_hline(y=cap_threshold, line_dash="dash", line_color="#EF4444", line_width=2, annotation_text=f"Regulatory Minimum ({cap_threshold:.1%})", annotation_position="bottom right")
    fig_cap.update_layout(
        xaxis_title="Reporting Period", yaxis_title="Capital Ratio", hovermode="x unified",
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"), height=400, **PLOTLY_LAYOUT
    )
    fig_cap.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    fig_cap.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
    st.plotly_chart(fig_cap, use_container_width=True)

    st.markdown('<div class="section-header">Current Capital Position</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        core_delta = kpi['core_cap_c'] - kpi['core_cap_p']
        st.metric("Core Capital (Tier I)", format_value(kpi['core_cap_c']), delta=f"{core_delta:+.4f}")
    with c2:
        total_delta = kpi['total_cap_c'] - kpi['total_cap_p']
        st.metric("Total Capital Ratio", format_value(kpi['total_cap_c']), delta=f"{total_delta:+.4f}")
    with c3:
        buffer_val = kpi["total_cap_c"] - cap_threshold
        st.metric("Capital Buffer", format_value(abs(buffer_val)), delta="Above minimum" if buffer_val > 0 else "Below minimum", delta_color="normal" if buffer_val > 0 else "inverse")

    if show_table:
        st.markdown('<div class="section-header">Compliance Status Report</div>', unsafe_allow_html=True)
        compliance_data = [
            {"Parameter": "Gross NPA", "Current": format_value(kpi["gross_npa_c"]), "Threshold": f"{npa_threshold:.1%}", "Status": "✓ Compliant" if kpi["gross_npa_c"] <= npa_threshold else "✗ Breach"},
            {"Parameter": "Net NPA", "Current": format_value(kpi["net_npa_c"]), "Threshold": f"{npa_threshold * 0.8:.1%}", "Status": "✓ Compliant" if kpi["net_npa_c"] <= npa_threshold * 0.8 else "✗ Breach"},
            {"Parameter": "Core Capital", "Current": format_value(kpi["core_cap_c"]), "Threshold": "5.50%", "Status": "✓ Compliant" if kpi["core_cap_c"] >= 0.055 else "✗ Breach"},
            {"Parameter": "Total Capital", "Current": format_value(kpi["total_cap_c"]), "Threshold": f"{cap_threshold:.1%}", "Status": "✓ Compliant" if kpi["total_cap_c"] >= cap_threshold else "✗ Breach"}
        ]
        st.dataframe(pd.DataFrame(compliance_data), use_container_width=True, hide_index=True)

# ── Tab 4: Data Explorer ──────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Interactive Data Explorer</div>', unsafe_allow_html=True)

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        part_filter = st.multiselect("Filter by Particulars", options=available_parts)
    with col_filter2:
        sort_col = st.selectbox("Sort By", options=["Month", "Particulars", "Rs"])

    explorer_df = df.copy()
    if part_filter:
        explorer_df = explorer_df[explorer_df["Particulars"].isin(part_filter)]
    explorer_df = explorer_df.sort_values(by=[sort_col, "Month"])

    col_display1, col_display2 = st.columns(2)
    with col_display1:
        rows_to_show = st.slider("Rows to Display", 5, 100, 25)
    with col_display2:
        st.download_button("📥 Export CSV", explorer_df.to_csv(index=False), "mis_data_export.csv", "text/csv", key='csv_download')

    st.markdown(f"Showing {min(rows_to_show, len(explorer_df))} of {len(explorer_df)} records")

    if show_raw:
        st.dataframe(explorer_df.head(rows_to_show), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">Pivot View</div>', unsafe_allow_html=True)
    if not explorer_df.empty:
        pivot = explorer_df.pivot_table(index="Particulars", columns="Month", values="Rs", aggfunc="first")
        st.dataframe(pivot, use_container_width=True)

    with st.expander("📊 Dataset Statistics"):
        st.write(f"**Total Rows:** {len(df)}")
        st.write(f"**Unique Metrics:** {df['Particulars'].nunique()}")
        st.write(f"**Time Periods:** {df['Month'].nunique()}")
        st.write(f"**Date Range:** {df['Month'].min()} to {df['Month'].max()}")

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 1rem;">
    <p style="margin: 0;">🏢 <strong>Basel Analytics</strong> | Executive MIS Dashboard</p>
    <p style="margin: 0.5rem 0 0 0;">
        Confidential Report | Generated: {dt} | FY 2025-26
    </p>
</div>
""".format(dt=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
