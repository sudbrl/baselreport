"""
Executive MIS Dashboard - Enhanced Version
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

# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="Executive MIS | Basel Analytics",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Custom CSS ----------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1E3A8A;
        --primary-light: #3B82F6;
        --secondary: #10B981;
        --danger: #EF4444;
        --warning: #F59E0B;
        --bg-dark: #0F172A;
        --bg-light: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --border: #E2E8F0;
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background: var(--bg-light); }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, var(--primary) 0%, #1a365d 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .header-title { font-size: 2rem; font-weight: 800; margin: 0; }
    .header-subtitle { opacity: 0.8; font-size: 1rem; margin-top: 0.5rem; }
    
    /* KPI Cards */
    .kpi-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid var(--primary);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .kpi-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .kpi-delta.positive { color: var(--secondary); }
    .kpi-delta.negative { color: var(--danger); }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-badge.safe { background: #D1FAE5; color: #065F46; }
    .status-badge.warning { background: #FEF3C7; color: #92400E; }
    .status-badge.danger { background: #FEE2E2; color: #991B1B; }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary);
    }
    
    /* Info cards */
    .info-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, var(--bg-dark) 0%, #1e293b 100%) !important; 
    }
    
    section[data-testid="stSidebar"] * { color: white !important; }
    
    .sidebar-section {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94A3B8;
        margin-bottom: 0.75rem;
    }
    
    /* Custom metric styling */
    div[data-testid="stMetric"] {
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    
    /* Tab styling */
    .stTabs button {
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Chart container */
    .chart-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Progress bar */
    .progress-container {
        background: #E2E8F0;
        border-radius: 9999px;
        height: 8px;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 9999px;
        transition: width 0.5s ease;
    }
    
    /* Alert boxes */
    .alert-box {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .alert-box.success { background: #D1FAE5; border-left: 4px solid #10B981; }
    .alert-box.warning { background: #FEF3C7; border-left: 4px solid #F59E0B; }
    .alert-box.danger { background: #FEE2E2; border-left: 4px solid #EF4444; }
    .alert-box.info { background: #DBEAFE; border-left: 4px solid #3B82F6; }
    
    /* Table styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .styled-table th {
        background: var(--primary);
        color: white;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .styled-table td {
        padding: 0.75rem;
        border-bottom: 1px solid var(--border);
        font-size: 0.9rem;
    }
    
    .styled-table tr:hover { background: #F1F5F9; }
    
    /* Hide streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Responsive containers */
    @media (max-width: 768px) {
        .kpi-card { margin-bottom: 1rem; }
        .header-title { font-size: 1.5rem; }
    }
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
        
        # Normalize column names
        df.columns = (
            df.columns.str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.replace('\xa0', ' ')
        )
        
        # Drop unnamed/helper columns
        drop_cols = [c for c in df.columns if c.startswith("Unnamed") 
                     or c in ("Helper", "Rs.1", "Rs.2", "Movements(%)")]
        df.drop(columns=drop_cols, errors="ignore", inplace=True)
        
        # Normalize text columns
        df["Month"]       = df["Month"].astype(str).str.strip()
        df["Particulars"] = df["Particulars"].astype(str).str.strip()
        
        return df
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Failed to load data. Please check your connection and try again.")
    st.stop()

# ---------------------- Row-based Lookup Utility ----------------------
def find_particular(df: pd.DataFrame, keywords: list[str]) -> str | None:
    for val in df["Particulars"].dropna().unique():
        val_lower = str(val).lower()
        if all(kw.lower() in val_lower for kw in keywords):
            return val
    return None

# Auto-detect row labels
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
    return float(result.iloc[0]) if not result.empty else 0.0

def get_series(particular_label: str) -> pd.DataFrame:
    return (
        df[df["Particulars"] == particular_label][["Month", "Rs"]]
        .copy()
        .reset_index(drop=True)
    )

def get_prev_month(month: str) -> str:
    months = df["Month"].dropna().unique().tolist()
    idx = months.index(month) if month in months else 0
    return months[max(0, idx - 1)]

def format_value(val: float) -> str:
    """Format value as percentage or number based on magnitude"""
    if abs(val) < 2:  # Likely a ratio
        return f"{val:.2%}"
    return f"{val:,.2f}"

def get_status(val: float, threshold: float, lower_better: bool = True) -> str:
    """Determine status based on threshold"""
    if lower_better:
        if val <= threshold: return "safe"
        elif val <= threshold * 1.2: return "warning"
        return "danger"
    else:
        if val >= threshold: return "safe"
        elif val >= threshold * 0.8: return "warning"
        return "danger"

def draw_gauge(value: float, max_value: float, title: str, threshold: float, 
               lower_better: bool = True, height: int = 200) -> go.Figure:
    """Create a gauge chart"""
    percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value * 100 if value < 1 else value,
        delta={"reference": threshold * 100 if threshold < 1 else threshold},
        gauge={
            "axis": {"range": [0, max_value * 100 if max_value < 1 else max_value * 1.5]},
            "bar": {"color": "#1E3A8A"},
            "steps": [
                {"range": [0, threshold * 0.7], "color": "#FEE2E2"},
                {"range": [threshold * 0.7, threshold], "color": "#FEF3C7"},
                {"range": [threshold, max_value], "color": "#D1FAE5"}
            ],
            "threshold": {
                "line": {"color": "#EF4444", "width": 4},
                "value": threshold
            }
        },
        number={"suffix": "%" if value < 1 else "", "font": {"size": 24}},
        title={"text": title, "font": {"size": 14}}
    ))
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# ---------------------- Sidebar Controls ----------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0; font-size: 1.5rem;">🏢 Basel Analytics</h2>
            <p style="opacity: 0.7; margin: 0.5rem 0 0 0;">MIS Dashboard v3.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # Report Controls
    st.markdown('<div class="sidebar-title">📊 Report Controls</div>', unsafe_allow_html=True)
    
    all_months = df["Month"].dropna().unique().tolist()
    selected_month = st.selectbox("Reporting Period", options=all_months, index=len(all_months) - 1)
    prev_month = get_prev_month(selected_month)
    
    available_parts = df["Particulars"].dropna().unique().tolist()
    selected_parts = st.multiselect("Select Metrics", options=available_parts,
                                     default=available_parts[:3] if len(available_parts) >= 3 else available_parts)
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # Analysis Options
    st.markdown('<div class="sidebar-title">🎛️ Analysis Options</div>', unsafe_allow_html=True)
    
    show_table = st.checkbox("Show Data Tables", value=True)
    show_raw = st.checkbox("Show Raw Data", value=False)
    comparison_periods = st.slider("Compare Last N Periods", 1, 6, 3)
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # Compliance Thresholds
    st.markdown('<div class="sidebar-title">⚠️ Compliance Thresholds</div>', unsafe_allow_html=True)
    
    npa_threshold = st.number_input("NPA Warning (%)", value=5.0, step=0.5) / 100
    cap_threshold = st.number_input("Capital Floor (%)", value=8.5, step=0.5) / 100
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # System Info
    st.markdown('<div class="sidebar-title">ℹ️ System</div>', unsafe_allow_html=True)
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption(f"Total Records: {len(df):,}")
    st.caption(f"Periods: {len(all_months)}")

# ---------------------- KPI Values ----------------------
kpi = {
    "gross_npa_c":  get_value(LABEL_GROSS_NPA,  selected_month),
    "gross_npa_p":  get_value(LABEL_GROSS_NPA,  prev_month),
    "net_npa_c":    get_value(LABEL_NET_NPA,     selected_month),
    "net_npa_p":    get_value(LABEL_NET_NPA,     prev_month),
    "core_cap_c":   get_value(LABEL_CORE_CAP,    selected_month),
    "core_cap_p":   get_value(LABEL_CORE_CAP,    prev_month),
    "total_cap_c":  get_value(LABEL_TOTAL_CAP,   selected_month),
    "total_cap_p":  get_value(LABEL_TOTAL_CAP,   prev_month),
}

# ---------------------- Header ----------------------
st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">📊 Executive MIS Dashboard</h1>
        <p class="header-subtitle">Financial Risk Intelligence Platform | Basel III Compliance Monitoring</p>
        <div style="display: flex; gap: 2rem; margin-top: 1rem; font-size: 0.9rem;">
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
    
    color_class = "positive" if improving else "negative"
    arrow = "↑" if delta > 0 else "↓"
    
    status = ""
    if threshold:
        status_class = get_status(current, threshold, lower_better)
        status_text = "✓ Safe" if status_class == "safe" else ("⚠ Warning" if status_class == "warning" else "✗ Alert")
        status = f'<span class="status-badge {status_class}">{status_text}</span>'
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{format_value(current)}</div>
        <div class="kpi-delta {color_class}">
            {arrow} {abs(delta)*100:.2f}% vs prior period
        </div>
        {status}
    </div>
    """

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(create_kpi_card("Gross NPA", kpi["gross_npa_c"], kpi["gross_npa_p"], 
                                 lower_better=True, threshold=npa_threshold), unsafe_allow_html=True)

with col2:
    st.markdown(create_kpi_card("Net NPA", kpi["net_npa_c"], kpi["net_npa_p"], 
                                 lower_better=True, threshold=npa_threshold), unsafe_allow_html=True)

with col3:
    st.markdown(create_kpi_card("Core Capital", kpi["core_cap_c"], kpi["core_cap_p"], 
                                 lower_better=False, threshold=5), unsafe_allow_html=True)

with col4:
    st.markdown(create_kpi_card("Capital Adequacy", kpi["total_cap_c"], kpi["total_cap_p"], 
                                 lower_better=False, threshold=cap_threshold), unsafe_allow_html=True)

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

# ---------------------- Main Tabs ----------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Performance Overview",
    "📉 Asset Quality", 
    "🛡️ Capital Compliance",
    "📋 Data Explorer"
])

# ── Tab 1: Performance Overview ───────────────────────────────────────────────
with tab1:
    # Time Series Chart
    st.markdown('<div class="section-header">📈 Multi-Metric Performance Trend</div>', unsafe_allow_html=True)
    
    if not selected_parts:
        st.warning("Please select metrics from the sidebar control panel.")
    else:
        trend_df = df[df["Particulars"].isin(selected_parts)].copy()
        
        fig1 = px.line(
            trend_df, x="Month", y="Rs", 
            color="Particulars",
            markers=True,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_traces(
            mode="lines+markers",
            marker=dict(size=10),
            line=dict(width=3)
        )
        fig1.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            xaxis_title="Reporting Period",
            yaxis_title="Value (₹)",
            height=400,
            margin=dict(b=80),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
        fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
        
        st.plotly_chart(fig1, use_container_width=True)
    
    # Period Comparison
    st.markdown('<div class="section-header">📊 Period-over-Period Comparison</div>', unsafe_allow_html=True)
    
    npa_gross_series = get_series(LABEL_GROSS_NPA)
    npa_net_series = get_series(LABEL_NET_NPA)
    
    # Create comparison chart
    fig_comp = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Gross NPA Trend", "Net NPA Trend"),
        horizontal_spacing=0.15
    )
    
    fig_comp.add_trace(
        go.Scatter(
            x=npa_gross_series["Month"], y=npa_gross_series["Rs"],
            name="Gross NPA",
            fill="tozeroy",
            line=dict(color="#1E3A8A", width=2),
            fillcolor="rgba(30, 58, 138, 0.2)"
        ),
        row=1, col=1
    )
    
    fig_comp.add_trace(
        go.Scatter(
            x=npa_net_series["Month"], y=npa_net_series["Rs"],
            name="Net NPA",
            fill="tozeroy",
            line=dict(color="#10B981", width=2),
            fillcolor="rgba(16, 185, 129, 0.2)"
        ),
        row=1, col=2
    )
    
    # Add threshold lines
    fig_comp.add_hline(y=npa_threshold, line_dash="dash", line_color="#EF4444", 
                       annotation_text=f"Threshold ({npa_threshold:.1%})", row=1, col=1)
    fig_comp.add_hline(y=npa_threshold, line_dash="dash", line_color="#EF4444", 
                       annotation_text=f"Threshold ({npa_threshold:.1%})", row=1, col=2)
    
    fig_comp.update_layout(height=350, showlegend=False, template="plotly_white")
    fig_comp.update_xaxes(title_text="Period")
    fig_comp.update_yaxes(title_text="Ratio")
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Summary Statistics
    if show_table:
        st.markdown('<div class="section-header">📋 Key Metrics Summary</div>', unsafe_allow_html=True)
        
        summary_data = []
        for label, db_label in [
            ("Gross NPA", LABEL_GROSS_NPA),
            ("Net NPA", LABEL_NET_NPA),
            ("Core Capital", LABEL_CORE_CAP),
            ("Total Capital", LABEL_TOTAL_CAP)
        ]:
            series = get_series(db_label)
            if len(series) > 0:
                summary_data.append({
                    "Metric": label,
                    "Current": format_value(series["Rs"].iloc[-1]),
                    "Previous": format_value(series["Rs"].iloc[-2]) if len(series) > 1 else "N/A",
                    "Change": f"{((series['Rs'].iloc[-1] / series['Rs'].iloc[-2]) - 1) * 100:.2f}%" if len(series) > 1 else "N/A",
                    "Min": format_value(series["Rs"].min()),
                    "Max": format_value(series["Rs"].max()),
                    "Average": format_value(series["Rs"].mean())
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ── Tab 2: Asset Quality ──────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">📉 Asset Quality Monitoring Dashboard</div>', unsafe_allow_html=True)
    
    # Gauge Charts Row
    g1, g2 = st.columns(2)
    
    with g1:
        fig_gross = draw_gauge(kpi["gross_npa_c"], 0.15, "Gross NPA Ratio", npa_threshold, lower_better=True)
        st.plotly_chart(fig_gross, use_container_width=True)
    
    with g2:
        fig_net = draw_gauge(kpi["net_npa_c"], 0.10, "Net NPA Ratio", npa_threshold * 0.8, lower_better=True)
        st.plotly_chart(fig_net, use_container_width=True)
    
    # NPA Classification Guide
    with st.expander("📚 NPA Classification Standards (Basel III)"):
        st.markdown("""
        | Category | Definition | Provisioning Rate |
        |----------|------------|-------------------|
        | **Standard** | Performing assets with timely repayment | 0.25% - 2.00% |
        | **Sub-Standard** | NPA for a period exceeding 90 days | 15% - 25% |
        | **Doubtful** | NPA for a period exceeding 12 months | 25% - 100% |
        | **Loss Asset** | Identified as non-recoverable | 100% |
        
        *Regulatory guidelines per Basel III framework*
        """)
    
    # Detailed NPA Chart
    st.markdown("### NPA Trend Analysis")
    
    fig_npa = go.Figure()
    
    fig_npa.add_trace(go.Bar(
        x=npa_gross_series["Month"],
        y=npa_gross_series["Rs"],
        name="Gross NPA",
        marker_color="#1E3A8A",
        text=npa_gross_series["Rs"].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:,.0f}"),
        textposition="outside"
    ))
    
    fig_npa.add_trace(go.Scatter(
        x=npa_net_series["Month"],
        y=npa_net_series["Rs"],
        name="Net NPA",
        mode="lines+markers+text",
        line=dict(color="#EF4444", width=3),
        marker=dict(size=12),
        text=npa_net_series["Rs"].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:,.0f}"),
        textposition="top center"
    ))
    
    fig_npa.update_layout(
        template="plotly_white",
        xaxis_title="Reporting Period",
        yaxis_title="NPA Ratio",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.15),
        height=400,
        barmode="group"
    )
    
    st.plotly_chart(fig_npa, use_container_width=True)
    
    # NPA Data Table
    if show_table:
        npa_combined = npa_gross_series.merge(npa_net_series, on="Month", suffixes=("_Gross", "_Net"))
        npa_combined.columns = ["Month", "Gross NPA", "Net NPA"]
        npa_combined["Spread"] = npa_combined["Gross NPA"] - npa_combined["Net NPA"]
        
        st.markdown("### NPA Data Summary")
        st.dataframe(npa_combined, use_container_width=True, hide_index=True)

# ── Tab 3: Capital Compliance ─────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">🛡️ Capital Adequacy & Compliance Analysis</div>', unsafe_allow_html=True)
    
    core_cap_series = get_series(LABEL_CORE_CAP)
    total_cap_series = get_series(LABEL_TOTAL_CAP)
    
    # Capital Gauges
    g1, g2, g3 = st.columns(3)
    
    with g1:
        fig_core = draw_gauge(kpi["core_cap_c"], 0.15, "Core Capital Ratio", 5.5, lower_better=False)
        st.plotly_chart(fig_core, use_container_width=True)
    
    with g2:
        fig_total = draw_gauge(kpi["total_cap_c"], 0.20, "Total Capital Ratio", cap_threshold, lower_better=False)
        st.plotly_chart(fig_total, use_container_width=True)
    
    with g3:
        buffer = kpi["total_cap_c"] - cap_threshold
        buffer_pct = (buffer / cap_threshold * 100) if cap_threshold > 0 else 0
        fig_buffer = draw_gauge(abs(buffer), cap_threshold * 0.5, "Capital Buffer", cap_threshold * 0.1, lower_better=False)
        st.plotly_chart(fig_buffer, use_container_width=True)
    
    # Combined Capital Chart
    st.markdown("### Capital Position Over Time")
    
    cap_df = core_cap_series.merge(total_cap_series, on="Month", suffixes=("_Core", "_Total"))
    cap_df.columns = ["Month", "Core Capital", "Total Capital"]
    
    fig_cap = go.Figure()
    
    fig_cap.add_trace(go.Scatter(
        x=cap_df["Month"], y=cap_df["Core Capital"],
        name="Core Capital (Tier I)",
        fill="tozeroy",
        mode="lines+markers",
        line=dict(color="#93C5FD", width=3),
        fillcolor="rgba(147, 197, 253, 0.3)"
    ))
    
    fig_cap.add_trace(go.Scatter(
        x=cap_df["Month"], y=cap_df["Total Capital"],
        name="Total Capital",
        fill="tonexty",
        mode="lines+markers",
        line=dict(color="#1E3A8A", width=3),
        fillcolor="rgba(30, 58, 138, 0.3)"
    ))
    
    # Regulatory floor annotation
    reg_floor = cap_threshold
    fig_cap.add_hline(
        y=reg_floor, 
        line_dash="dash", 
        line_color="#EF4444",
        line_width=2,
        annotation_text=f"Regulatory Minimum ({reg_floor:.1%})",
        annotation_position="bottom right"
    )
    
    fig_cap.update_layout(
        template="plotly_white",
        xaxis_title="Reporting Period",
        yaxis_title="Capital Ratio",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1),
        height=400,
        annotations=[
            dict(x=0, y=reg_floor, xref="paper", yref="y", 
                 text=f"Min: {reg_floor:.1%}", showarrow=True, arrowhead=2)
        ]
    )
    
    st.plotly_chart(fig_cap, use_container_width=True)
    
    # Capital Metrics Cards
    st.markdown("### Current Capital Position")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        core_delta = kpi['core_cap_c'] - kpi['core_cap_p']
        st.metric("Core Capital (Tier I)", format_value(kpi['core_cap_c']),
                  delta=f"{core_delta:+.4f}" if kpi['core_cap_c'] < 2 else f"{core_delta:+,.2f}")
    
    with c2:
        total_delta = kpi['total_cap_c'] - kpi['total_cap_p']
        st.metric("Total Capital Ratio", format_value(kpi['total_cap_c']),
                  delta=f"{total_delta:+.4f}" if kpi['total_cap_c'] < 2 else f"{total_delta:+,.2f}")
    
    with c3:
        buffer_val = kpi["total_cap_c"] - cap_threshold
        st.metric("Capital Buffer", format_value(abs(buffer_val)),
                  delta="Above minimum" if buffer_val > 0 else "Below minimum",
                  delta_color="normal" if buffer_val > 0 else "inverse")
    
    # Compliance Status Table
    if show_table:
        st.markdown("### Compliance Status Report")
        
        compliance_data = [
            {"Parameter": "Gross NPA", "Current": format_value(kpi["gross_npa_c"]),
             "Threshold": f"{npa_threshold:.1%}",
             "Status": "✓ Compliant" if kpi["gross_npa_c"] <= npa_threshold else "✗ Breach"},
            {"Parameter": "Net NPA", "Current": format_value(kpi["net_npa_c"]),
             "Threshold": f"{npa_threshold * 0.8:.1%}",
             "Status": "✓ Compliant" if kpi["net_npa_c"] <= npa_threshold * 0.8 else "✗ Breach"},
            {"Parameter": "Core Capital", "Current": format_value(kpi["core_cap_c"]),
             "Threshold": "5.5%",
             "Status": "✓ Compliant" if kpi["core_cap_c"] >= 0.055 else "✗ Breach"},
            {"Parameter": "Total Capital", "Current": format_value(kpi["total_cap_c"]),
             "Threshold": f"{cap_threshold:.1%}",
             "Status": "✓ Compliant" if kpi["total_cap_c"] >= cap_threshold else "✗ Breach"}
        ]
        
        st.dataframe(pd.DataFrame(compliance_data), use_container_width=True, hide_index=True)

# ── Tab 4: Data Explorer ──────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">📋 Interactive Data Explorer</div>', unsafe_allow_html=True)
    
    # Filters
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        part_filter = st.multiselect("Filter by Particulars", options=available_parts)
    
    with col_filter2:
        sort_col = st.selectbox("Sort By", options=["Month", "Particulars", "Rs"])
    
    # Apply filters
    explorer_df = df.copy()
    
    if part_filter:
        explorer_df = explorer_df[explorer_df["Particulars"].isin(part_filter)]
    
    explorer_df = explorer_df.sort_values(by=[sort_col, "Month"])
    
    # Display options
    col_display1, col_display2 = st.columns(2)
    
    with col_display1:
        rows_to_show = st.slider("Rows to Display", 5, 100, 25)
    
    with col_display2:
        st.download_button(
            "📥 Export CSV",
            explorer_df.to_csv(index=False),
            "mis_data_export.csv",
            "text/csv",
            key='csv_download'
        )
    
    st.markdown(f"Showing {min(rows_to_show, len(explorer_df))} of {len(explorer_df)} records")
    
    # Data table with formatting
    if show_raw:
        st.dataframe(
            explorer_df.head(rows_to_show),
            use_container_width=True,
            hide_index=True
        )
    
    # Pivot Table View
    st.markdown("### Pivot View")
    
    if not explorer_df.empty:
        pivot = explorer_df.pivot_table(
            index="Particulars",
            columns="Month",
            values="Rs",
            aggfunc="first"
        )
        st.dataframe(pivot, use_container_width=True)
    
    # Statistics
    with st.expander("📊 Dataset Statistics"):
        st.write(f"**Total Rows:** {len(df)}")
        st.write(f"**Unique Metrics:** {df['Particulars'].nunique()}")
        st.write(f"**Time Periods:** {df['Month'].nunique()}")
        st.write(f"**Date Range:** {df['Month'].min()} to {df['Month'].max()}")

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 1rem;">
    <p style="margin: 0;">🏢 <strong>Basel Analytics</strong> | Executive MIS Dashboard</p>
    <p style="margin: 0.5rem 0 0 0;">
        Confidential Report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | FY 2025-26
    </p>
</div>
""", unsafe_allow_html=True)
