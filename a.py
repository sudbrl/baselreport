"""
Executive MIS Dashboard - Basel Analytics
Enterprise-grade Financial Risk Intelligence Platform

Author: Basel Analytics Team
Version: 5.0.0
Last Updated: 2026-02-15

ENHANCEMENTS:
- Professional data labels on all charts
- Enhanced color schemes and typography
- Improved data visualization with annotations
- Better user guidance and tooltips
- Responsive design improvements
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime, timedelta
import requests
import logging
from typing import Tuple, Optional, List
import numpy as np

# ---------------------- Logging Configuration ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------- Constants & Configuration ----------------------
class Config:
    """Application configuration constants"""
    PAGE_TITLE = "Executive MIS | Basel Analytics"
    PAGE_ICON = "🏢"
    LAYOUT = "wide"
    DATA_SOURCE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    CACHE_TTL = 3600  # 1 hour
    VERSION = "5.0.0"
    FISCAL_YEAR = "2025-26"
    
    # Regulatory thresholds
    MIN_CORE_CAPITAL = 0.06  # 6%
    MIN_TOTAL_CAPITAL = 0.085  # 8.5%
    TARGET_GNPA = 0.03  # 3%
    TARGET_NNPA = 0.01  # 1%
    
    # Enhanced color palette
    COLORS = {
        'primary': '#1E3A8A',
        'secondary': '#3B82F6',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'info': '#06B6D4',
        'neutral': '#64748B',
        'chart_palette': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#EC4899', '#14B8A6']
    }

# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state="expanded"
)

# ---------------------- Enhanced Professional Theme & CSS ----------------------
st.markdown("""
<style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Color Palette */
    :root { 
        --primary: #1E3A8A; 
        --primary-light: #3B82F6;
        --secondary: #0F172A;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --info: #06B6D4;
        --bg: #F8FAFC;
        --bg-secondary: #F1F5F9;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --border: #E2E8F0;
    }
    
    /* Main Container */
    .main { 
        background-color: var(--bg); 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        padding-top: 1rem;
    }
    
    /* Enhanced KPI Card Styling with Gradient */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.75rem;
        border-radius: 16px;
        border-left: 5px solid var(--primary);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(59,130,246,0.05) 0%, rgba(16,185,129,0.05) 100%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
    }
    
    .metric-label { 
        font-size: 0.75rem; 
        color: var(--text-secondary); 
        font-weight: 700; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .metric-value { 
        font-size: 2.25rem; 
        font-weight: 800; 
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        background: rgba(0,0,0,0.05);
        border-radius: 6px;
        display: inline-flex;
        margin-top: 0.5rem;
    }
    
    /* Alert Boxes with Icons */
    .alert-box {
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .alert-icon {
        font-size: 1.5rem;
        line-height: 1;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-color: var(--warning);
        color: #92400E;
    }
    
    .alert-danger {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        border-color: var(--danger);
        color: #991B1B;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        border-color: var(--success);
        color: #065F46;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #CFFAFE 0%, #A5F3FC 100%);
        border-color: var(--info);
        color: #164E63;
    }
    
    /* Enhanced Sidebar */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important;
    }
    
    section[data-testid="stSidebar"] * { 
        color: white !important; 
    }
    
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(59,130,246,0.3);
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59,130,246,0.4);
    }
    
    /* Tab Styling Enhancement */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 1.5rem;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
    }
    
    /* Enhanced Table Styling */
    .dataframe {
        border: none !important;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        padding: 1.25rem 1rem !important;
        letter-spacing: 0.5px;
    }
    
    .dataframe tbody tr {
        transition: background-color 0.2s;
    }
    
    .dataframe tbody tr:hover {
        background-color: #EFF6FF !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: var(--bg-secondary);
    }
    
    .dataframe tbody td {
        padding: 1rem !important;
        font-size: 0.9rem;
    }
    
    /* Header Enhancement */
    h1 {
        color: var(--primary);
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: var(--text-primary);
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: var(--text-primary);
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, white 100%);
        border-radius: 10px;
        font-weight: 600;
        padding: 1rem 1.5rem;
        border: 1px solid var(--border);
        transition: all 0.3s;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #E0E7FF 0%, var(--bg-secondary) 100%);
        border-color: var(--primary-light);
    }
    
    /* Info Box Styling */
    .info-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid var(--info);
        padding: 1.25rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    
    /* Metric Badge */
    .metric-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background-color: #D1FAE5;
        color: #065F46;
    }
    
    .badge-warning {
        background-color: #FEF3C7;
        color: #92400E;
    }
    
    .badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    
    /* Loading State */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }
    
    /* Tooltip Enhancement */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        border-bottom: 1px dotted var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Access Layer ----------------------
@st.cache_data(ttl=Config.CACHE_TTL, show_spinner=False)
def load_mis_data() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Load MIS data from remote Excel file with comprehensive error handling"""
    try:
        logger.info(f"Fetching data from {Config.DATA_SOURCE_URL}")
        
        response = requests.get(Config.DATA_SOURCE_URL, timeout=30)
        response.raise_for_status()
        
        xls = pd.ExcelFile(BytesIO(response.content))
        
        # Load and clean main data
        df_main = xls.parse("Data")
        columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
        df_main = df_main.drop(columns=columns_to_drop, errors="ignore")
        
        # Validate critical columns
        required_columns = ["Month", "Particulars", "Rs"]
        if not all(col in df_main.columns for col in required_columns):
            raise ValueError(f"Missing required columns in main data. Expected: {required_columns}")
        
        # Load NPA and Capital data
        df_npa = xls.parse("Sheet1")
        df_cap = xls.parse("capital")
        
        # Data validation
        df_main = df_main.dropna(subset=["Month"])
        df_npa = df_npa.dropna(subset=["Month"])
        df_cap = df_cap.dropna(subset=["Month"])
        
        # Convert percentage columns properly
        for col in df_npa.columns:
            if "Npa" in col or "%" in col:
                df_npa[col] = pd.to_numeric(df_npa[col], errors='coerce')
        
        for col in df_cap.columns:
            if "%" in col:
                df_cap[col] = pd.to_numeric(df_cap[col], errors='coerce')
        
        logger.info(f"Successfully loaded {len(df_main)} main records, {len(df_npa)} NPA records, {len(df_cap)} capital records")
        
        return df_main, df_npa, df_cap
        
    except requests.RequestException as e:
        logger.error(f"Network error loading data: {e}")
        st.error("🚨 **Network Error**: Unable to fetch data from server. Please check your connection.")
        return None, None, None
    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        st.error(f"🚨 **Data Validation Error**: {e}")
        return None, None, None
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}", exc_info=True)
        st.error(f"🚨 **System Error**: {str(e)}")
        return None, None, None

# ---------------------- Utility Functions ----------------------
def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate percentage growth rate"""
    if previous == 0:
        return 0.0
    return ((current - previous) / abs(previous))

def format_currency(value: float, compact: bool = True) -> str:
    """Format currency values with Indian numbering system"""
    if pd.isna(value):
        return "N/A"
    
    if compact:
        if abs(value) >= 10000000:  # Crores
            return f"₹{value/10000000:.2f}Cr"
        elif abs(value) >= 100000:  # Lakhs
            return f"₹{value/100000:.2f}L"
        elif abs(value) >= 1000:  # Thousands
            return f"₹{value/1000:.2f}K"
    
    return f"₹{value:,.2f}"

def get_risk_status(value: float, threshold: float, lower_is_better: bool = True) -> str:
    """Determine risk status based on threshold"""
    if lower_is_better:
        if value <= threshold:
            return "success"
        elif value <= threshold * 1.5:
            return "warning"
        else:
            return "danger"
    else:
        if value >= threshold:
            return "success"
        elif value >= threshold * 0.75:
            return "warning"
        else:
            return "danger"

def create_alert_box(message: str, alert_type: str = "warning") -> None:
    """Create styled alert box with icon"""
    icons = {
        'warning': '⚠️',
        'danger': '🚨',
        'success': '✅',
        'info': 'ℹ️'
    }
    
    st.markdown(f"""
        <div class="alert-box alert-{alert_type}">
            <div class="alert-icon">{icons.get(alert_type, 'ℹ️')}</div>
            <div><strong>{message}</strong></div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Enhanced KPI Component ----------------------
def render_kpi_card(label: str, current: float, previous: float, 
                   format_type: str = "percent", lower_better: bool = False,
                   threshold: Optional[float] = None, icon: str = "📊") -> None:
    """Render enhanced KPI card with trend analysis and icon"""
    delta = current - previous
    delta_pct = calculate_growth_rate(current, previous)
    
    # Determine color based on performance
    if threshold:
        status = get_risk_status(current, threshold, lower_better)
        border_color = {"success": "#10B981", "warning": "#F59E0B", "danger": "#EF4444"}[status]
    else:
        is_positive = (delta < 0 and lower_better) or (delta > 0 and not lower_better)
        border_color = "#10B981" if is_positive else "#EF4444"
    
    color = "#10B981" if (delta < 0 and lower_better) or (delta > 0 and not lower_better) else "#EF4444"
    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "●"
    
    # Format values
    if format_type == "percent":
        current_display = f"{current:.2%}"
        delta_display = f"{abs(delta_pct)*100:.2f}%"
    else:
        current_display = format_currency(current)
        delta_display = format_currency(abs(delta))
    
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {border_color};">
            <div class="metric-label">
                <span style="font-size: 1.25rem;">{icon}</span>
                <span>{label}</span>
            </div>
            <div class="metric-value">{current_display}</div>
            <div class="metric-delta" style="color: {color};">
                <span style="font-size: 1.2rem;">{arrow}</span>
                <span>{delta_display}</span>
                <span style="color: #94A3B8; font-weight: normal;">vs Previous</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Load Data ----------------------
with st.spinner("🔄 Loading MIS data from secure server..."):
    df_main, df_npa, df_cap = load_mis_data()

if df_main is None or df_npa is None or df_cap is None:
    st.stop()

# ---------------------- Enhanced Sidebar Controls ----------------------
with st.sidebar:
    st.markdown("### 🎛️ CONTROL CENTER")
    st.markdown("---")
    
    # Period Selection
    st.markdown("##### 📅 REPORTING PERIOD")
    all_months = sorted(df_main["Month"].unique().tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox(
            "Current Period", 
            options=all_months, 
            index=len(all_months)-1,
            key="month_selector",
            help="Select the reporting period for analysis"
        )
    
    with col2:
        comparison_options = ["Previous Month", "Previous Quarter", "Previous Year"]
        comparison_period = st.selectbox(
            "Compare to", 
            comparison_options, 
            key="comparison",
            help="Select comparison period"
        )
    
    st.markdown("---")
    
    # Metric Selection with improved UX
    st.markdown("##### 📊 METRIC FILTERS")
    
    available_parts = sorted(df_main["Particulars"].dropna().unique().tolist())
    
    # Categorize metrics
    asset_metrics = [p for p in available_parts if any(x in p.lower() for x in ['advance', 'loan', 'asset'])]
    liability_metrics = [p for p in available_parts if any(x in p.lower() for x in ['deposit', 'liability', 'borrowing'])]
    other_metrics = [p for p in available_parts if p not in asset_metrics and p not in liability_metrics]
    
    metric_category = st.radio(
        "Category", 
        ["All", "Assets", "Liabilities", "Others"], 
        key="category",
        help="Filter metrics by category",
        horizontal=True
    )
    
    if metric_category == "Assets":
        metric_pool = asset_metrics
    elif metric_category == "Liabilities":
        metric_pool = liability_metrics
    elif metric_category == "Others":
        metric_pool = other_metrics
    else:
        metric_pool = available_parts
    
    # Quick selection buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Select All", use_container_width=True, help="Select all metrics in category"):
            st.session_state.select_all = True
    with col_b:
        if st.button("Clear All", use_container_width=True, help="Clear all selections"):
            st.session_state.clear_all = True
    
    # Handle quick selection
    if 'select_all' in st.session_state and st.session_state.select_all:
        default_selection = metric_pool
        st.session_state.select_all = False
    elif 'clear_all' in st.session_state and st.session_state.clear_all:
        default_selection = []
        st.session_state.clear_all = False
    else:
        default_selection = metric_pool[:3] if len(metric_pool) >= 3 else metric_pool
    
    selected_parts = st.multiselect(
        "Select Metrics", 
        options=metric_pool,
        default=default_selection,
        key="metrics",
        help="Choose metrics to display in performance charts"
    )
    
    st.markdown("---")
    
    # Display Options
    st.markdown("##### 🎨 DISPLAY OPTIONS")
    show_data_labels = st.checkbox("Show Data Labels", value=True, help="Display values on charts")
    show_trend_lines = st.checkbox("Show Trend Lines", value=False, help="Add trend lines to charts")
    chart_height = st.slider("Chart Height", 300, 700, 500, 50, help="Adjust chart height")
    
    st.markdown("---")
    
    # Export Options
    st.markdown("##### 📥 EXPORT & REPORTS")
    export_format = st.selectbox("Format", ["Excel", "CSV", "PDF"], key="export_format")
    
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("📝 Report generation feature will be available in the next release")
    
    st.markdown("---")
    
    # System Info with enhanced styling
    st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 1.25rem; border-radius: 10px; font-size: 0.8rem;'>
            <div style='font-weight: 700; margin-bottom: 0.75rem; font-size: 0.75rem; letter-spacing: 1px;'>SYSTEM INFO</div>
            <div style='margin-bottom: 0.5rem;'><strong>Version:</strong> v{Config.VERSION}</div>
            <div style='margin-bottom: 0.5rem;'><strong>Fiscal Year:</strong> {Config.FISCAL_YEAR}</div>
            <div style='margin-bottom: 0.5rem;'><strong>Last Update:</strong> {datetime.now().strftime('%H:%M:%S')}</div>
            <div style='margin-bottom: 0.5rem;'><strong>Data Points:</strong> {len(df_main):,}</div>
            <div style='margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.2);'>
                <strong>Status:</strong> <span style='color: #10B981;'>● Active</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Calculate KPI Indices ----------------------
try:
    c_idx = df_npa[df_npa['Month'] == selected_month].index[0]
    p_idx = max(0, c_idx - 1)
    
    # Get actual values
    current_gnpa = df_npa.loc[c_idx, "Gross Npa To Gross Advances"]
    current_nnpa = df_npa.loc[c_idx, "Net Npa To Net Advances"]
    current_core_cap = df_cap.loc[c_idx, "Core Capital%"]
    current_total_cap = df_cap.loc[c_idx, "Total Capital%"]
    
    prev_gnpa = df_npa.loc[p_idx, "Gross Npa To Gross Advances"]
    prev_nnpa = df_npa.loc[p_idx, "Net Npa To Net Advances"]
    prev_core_cap = df_cap.loc[p_idx, "Core Capital%"]
    prev_total_cap = df_cap.loc[p_idx, "Total Capital%"]
    
except (IndexError, KeyError) as e:
    logger.error(f"Error accessing period data: {e}")
    st.error("⚠️ Selected period data not available")
    st.stop()

# ---------------------- Enhanced Header Section ----------------------
col_title, col_status = st.columns([3, 1])

with col_title:
    st.markdown("# 📊 Financial Risk Intelligence Dashboard")
    st.markdown(f"""
        <div style='font-size: 1rem; color: #64748B; margin-bottom: 1rem;'>
            <strong>Reporting Period:</strong> <span style='color: #1E3A8A; font-weight: 600;'>{selected_month}</span> | 
            <strong>Comparison:</strong> <span style='color: #1E3A8A; font-weight: 600;'>{comparison_period}</span>
        </div>
    """, unsafe_allow_html=True)

with col_status:
    # Overall health indicator with enhanced design
    issues = 0
    if current_gnpa > Config.TARGET_GNPA:
        issues += 1
    if current_total_cap < Config.MIN_TOTAL_CAPITAL:
        issues += 1
    
    if issues == 0:
        health_status = "Healthy"
        health_color = "#10B981"
        health_icon = "🟢"
    elif issues == 1:
        health_status = "Monitor"
        health_color = "#F59E0B"
        health_icon = "🟡"
    else:
        health_status = "Alert"
        health_color = "#EF4444"
        health_icon = "🔴"
    
    st.markdown(f"""
        <div style='text-align: right; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <div style='font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>SYSTEM STATUS</div>
            <div style='font-size: 1.5rem; font-weight: 800; color: {health_color}; display: flex; align-items: center; justify-content: flex-end; gap: 0.5rem;'>
                <span>{health_icon}</span>
                <span>{health_status}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------- KPI Dashboard with Icons ----------------------
st.markdown("### 🎯 Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

with k1:
    render_kpi_card(
        "Gross NPA Ratio", 
        current_gnpa, 
        prev_gnpa, 
        lower_better=True,
        threshold=Config.TARGET_GNPA,
        icon="📉"
    )

with k2:
    render_kpi_card(
        "Net NPA Ratio", 
        current_nnpa, 
        prev_nnpa, 
        lower_better=True,
        threshold=Config.TARGET_NNPA,
        icon="📊"
    )

with k3:
    render_kpi_card(
        "Tier 1 Capital", 
        current_core_cap, 
        prev_core_cap,
        threshold=Config.MIN_CORE_CAPITAL,
        icon="🛡️"
    )

with k4:
    render_kpi_card(
        "Total CAR", 
        current_total_cap, 
        prev_total_cap,
        threshold=Config.MIN_TOTAL_CAPITAL,
        icon="💰"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------- Enhanced Alert System ----------------------
st.markdown("### 🚨 Risk Alerts & Compliance Status")

alert_col1, alert_col2 = st.columns(2)

with alert_col1:
    if current_gnpa > Config.TARGET_GNPA:
        create_alert_box(
            f"Gross NPA at {current_gnpa:.2%} exceeds target of {Config.TARGET_GNPA:.2%}. "
            f"Immediate review of loan portfolio required.",
            "danger" if current_gnpa > Config.TARGET_GNPA * 1.5 else "warning"
        )
    else:
        create_alert_box(f"Gross NPA within acceptable limits at {current_gnpa:.2%}", "success")

with alert_col2:
    if current_total_cap < Config.MIN_TOTAL_CAPITAL:
        create_alert_box(
            f"Capital Adequacy at {current_total_cap:.2%} below regulatory minimum of {Config.MIN_TOTAL_CAPITAL:.2%}. "
            f"Capital infusion required.",
            "danger"
        )
    else:
        buffer = current_total_cap - Config.MIN_TOTAL_CAPITAL
        create_alert_box(
            f"Capital Adequacy compliant with {buffer:.2%} buffer above minimum",
            "success"
        )

st.markdown("---")

# ---------------------- Main Content Tabs ----------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Performance Analytics", 
    "🔍 Asset Quality", 
    "🛡️ Capital Compliance",
    "📑 Executive Summary"
])

# ---------------------- Tab 1: Performance Analytics with Enhanced Data Labels ----------------------
with tab1:
    st.markdown("### 📊 Multi-Period Performance Analysis")
    
    if not selected_parts:
        st.markdown("""
            <div class="info-box">
                <strong>ℹ️ Getting Started:</strong> Please select at least one metric from the sidebar 
                (under "Metric Filters") to view performance trends and analytics.
            </div>
        """, unsafe_allow_html=True)
    else:
        # Trend Analysis with Professional Data Labels
        trend_df = df_main[df_main["Particulars"].isin(selected_parts)].copy()
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create enhanced chart with data labels
        fig_trend = go.Figure()
        
        colors = Config.COLORS['chart_palette']
        
        for idx, particular in enumerate(selected_parts):
            data = trend_df[trend_df["Particulars"] == particular].sort_values("Month")
            
            # Add line trace
            fig_trend.add_trace(
                go.Scatter(
                    x=data["Month"],
                    y=data["Rs"],
                    name=particular,
                    mode="lines+markers" + ("+text" if show_data_labels else ""),
                    line=dict(width=3, color=colors[idx % len(colors)]),
                    marker=dict(
                        size=10,
                        color=colors[idx % len(colors)],
                        line=dict(color='white', width=2)
                    ),
                    text=data["Rs"].apply(lambda x: format_currency(x)) if show_data_labels else None,
                    textposition="top center",
                    textfont=dict(size=10, color=colors[idx % len(colors)], family="Inter"),
                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                "Period: <b>%{x}</b><br>" +
                                "Amount: <b>₹%{y:,.0f}</b><br>" +
                                "<extra></extra>"
                )
            )
            
            # Add trend line if enabled
            if show_trend_lines and len(data) > 2:
                z = np.polyfit(range(len(data)), data["Rs"], 1)
                p = np.poly1d(z)
                fig_trend.add_trace(
                    go.Scatter(
                        x=data["Month"],
                        y=p(range(len(data))),
                        name=f"{particular} (Trend)",
                        mode="lines",
                        line=dict(width=2, color=colors[idx % len(colors)], dash='dash'),
                        opacity=0.5,
                        showlegend=True,
                        hoverinfo='skip'
                    )
                )
        
        fig_trend.update_layout(
            template="plotly_white",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="#E2E8F0",
                borderwidth=2,
                font=dict(size=11, family="Inter")
            ),
            xaxis=dict(
                title="<b>Period</b>",
                showgrid=True,
                gridcolor="#F1F5F9",
                title_font=dict(size=13, family="Inter", color="#1E3A8A")
            ),
            yaxis=dict(
                title="<b>Amount (₹)</b>",
                showgrid=True,
                gridcolor="#F1F5F9",
                tickformat=",.0f",
                title_font=dict(size=13, family="Inter", color="#1E3A8A")
            ),
            height=chart_height,
            margin=dict(t=50, b=120, l=80, r=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter")
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance Summary Table with Enhanced Styling
        st.markdown("#### 📋 Performance Summary")
        
        summary_data = []
        for particular in selected_parts:
            data = trend_df[trend_df["Particulars"] == particular].sort_values("Month")
            if len(data) >= 2:
                latest = data.iloc[-1]["Rs"]
                previous = data.iloc[-2]["Rs"]
                growth = calculate_growth_rate(latest, previous)
                
                # Calculate additional metrics
                avg_value = data["Rs"].mean()
                max_value = data["Rs"].max()
                min_value = data["Rs"].min()
                
                summary_data.append({
                    "Metric": particular,
                    "Current": format_currency(latest, compact=False),
                    "Previous": format_currency(previous, compact=False),
                    "Growth %": f"{growth*100:+.2f}%",
                    "Average": format_currency(avg_value, compact=False),
                    "Peak": format_currency(max_value, compact=False),
                    "Trend": "📈 Upward" if growth > 0.05 else "📉 Downward" if growth < -0.05 else "➡️ Stable"
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(
                summary_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download option
            csv = summary_df.to_csv(index=False)
            st.download_button(
                "📥 Download Summary (CSV)",
                csv,
                "performance_summary.csv",
                "text/csv",
                key='download-csv'
            )

# ---------------------- Tab 2: Asset Quality with Enhanced Visualizations ----------------------
with tab2:
    st.markdown("### 🔍 Non-Performing Asset Analysis")
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Enhanced NPA Trend Chart with Data Labels
    fig_npa = go.Figure()
    
    # Gross NPA - Bars with data labels
    fig_npa.add_trace(go.Bar(
        x=df_npa["Month"],
        y=df_npa["Gross Npa To Gross Advances"],
        name="Gross NPA",
        marker=dict(
            color='#3B82F6',
            line=dict(color='#1E3A8A', width=1.5),
            pattern_shape="",
        ),
        text=df_npa["Gross Npa To Gross Advances"].apply(lambda x: f'{x:.2%}') if show_data_labels else None,
        textposition='outside',
        textfont=dict(size=11, color='#1E3A8A', family="Inter", weight='bold'),
        hovertemplate="<b>Gross NPA</b><br>" +
                     "Period: <b>%{x}</b><br>" +
                     "Ratio: <b>%{y:.2%}</b><br>" +
                     "<extra></extra>"
    ))
    
    # Net NPA - Line with enhanced markers and data labels
    fig_npa.add_trace(go.Scatter(
        x=df_npa["Month"],
        y=df_npa["Net Npa To Net Advances"],
        name="Net NPA",
        mode='lines+markers' + ('+text' if show_data_labels else ''),
        line=dict(color='#EF4444', width=4),
        marker=dict(
            size=12, 
            symbol='diamond',
            color='#EF4444',
            line=dict(color='white', width=2)
        ),
        text=df_npa["Net Npa To Net Advances"].apply(lambda x: f'{x:.2%}') if show_data_labels else None,
        textposition='top center',
        textfont=dict(size=11, color='#EF4444', family="Inter", weight='bold'),
        hovertemplate="<b>Net NPA</b><br>" +
                     "Period: <b>%{x}</b><br>" +
                     "Ratio: <b>%{y:.2%}</b><br>" +
                     "<extra></extra>"
    ))
    
    # Enhanced target line with annotation
    fig_npa.add_hline(
        y=Config.TARGET_GNPA,
        line_dash="dash",
        line_color="#F59E0B",
        line_width=2,
        annotation=dict(
            text=f"<b>Target: {Config.TARGET_GNPA:.1%}</b>",
            font=dict(size=12, color="#F59E0B", family="Inter"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#F59E0B",
            borderwidth=2,
            borderpad=4
        ),
        annotation_position="right"
    )
    
    fig_npa.update_layout(
        template="plotly_white",
        yaxis_tickformat=".2%",
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>NPA Ratio</b>",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#E2E8F0",
            borderwidth=2,
            font=dict(size=11, family="Inter")
        ),
        height=chart_height,
        margin=dict(t=40, b=100, l=80, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            title_font=dict(size=13, family="Inter", color="#1E3A8A")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            title_font=dict(size=13, family="Inter", color="#1E3A8A")
        )
    )
    
    st.plotly_chart(fig_npa, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # NPA Statistics with enhanced cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        npa_movement = current_gnpa - prev_gnpa
        st.metric(
            "Gross NPA Movement",
            f"{npa_movement:+.2%}",
            delta=f"{'Improvement' if npa_movement < 0 else 'Deterioration'}",
            delta_color="inverse" if npa_movement < 0 else "normal"
        )
    
    with col2:
        provision_coverage = (1 - (current_nnpa / current_gnpa)) if current_gnpa > 0 else 0
        st.metric(
            "Provision Coverage",
            f"{provision_coverage:.1%}",
            delta="Strong" if provision_coverage > 0.7 else "Needs Improvement"
        )
    
    with col3:
        avg_npa = df_npa["Gross Npa To Gross Advances"].mean()
        vs_avg = current_gnpa - avg_npa
        st.metric(
            "vs Portfolio Average",
            f"{vs_avg:+.2%}",
            delta="Below avg" if vs_avg < 0 else "Above avg",
            delta_color="inverse" if vs_avg < 0 else "normal"
        )
    
    # Asset Classification Framework
    with st.expander("📚 Asset Classification & Provisioning Framework", expanded=False):
        st.markdown("""
        #### Basel III Asset Classification Standards
        
        The following framework is used for loan classification and provisioning determination:
        """)
        
        classification_data = {
            "Category": ["Standard", "Sub-Standard", "Doubtful", "Loss"],
            "Definition": [
                "No default, regular servicing",
                "Overdue > 90 days",
                "Overdue > 12 months",
                "Identified as non-recoverable"
            ],
            "Provisioning Range": [
                "0.25% - 2.00%",
                "15.00% - 25.00%",
                "25.00% - 100.00%",
                "100.00%"
            ],
            "Risk Weight": [
                "20% - 150%",
                "100%",
                "100% - 150%",
                "150%"
            ]
        }
        
        st.table(pd.DataFrame(classification_data))
        
        st.markdown("""
            <div class="info-box">
                <strong>💡 Regulatory Note:</strong> Provisioning requirements are as per RBI guidelines 
                and Basel III framework. Regular monitoring ensures compliance with regulatory standards.
            </div>
        """, unsafe_allow_html=True)

# ---------------------- Tab 3: Capital Compliance with Enhanced Charts ----------------------
with tab3:
    st.markdown("### 🛡️ Capital Adequacy & Regulatory Compliance")
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Enhanced Capital Adequacy Chart
    fig_cap = go.Figure()
    
    # Core Capital - Area with data labels
    fig_cap.add_trace(go.Scatter(
        x=df_cap["Month"],
        y=df_cap["Core Capital%"],
        name="Tier 1 Capital",
        fill='tonexty',
        mode='lines+markers' + ('+text' if show_data_labels else ''),
        line=dict(color='#3B82F6', width=3),
        marker=dict(
            size=10, 
            color='#3B82F6',
            line=dict(color='white', width=2)
        ),
        text=df_cap["Core Capital%"].apply(lambda x: f'{x:.1%}') if show_data_labels else None,
        textposition='top center',
        textfont=dict(size=10, color='#1E3A8A', family="Inter"),
        hovertemplate="<b>Tier 1 Capital</b><br>" +
                     "Period: <b>%{x}</b><br>" +
                     "Ratio: <b>%{y:.2%}</b><br>" +
                     "<extra></extra>"
    ))
    
    # Total Capital - Area with enhanced styling and data labels
    fig_cap.add_trace(go.Scatter(
        x=df_cap["Month"],
        y=df_cap["Total Capital%"],
        name="Total Capital (CAR)",
        fill='tonexty',
        mode='lines+markers' + ('+text' if show_data_labels else ''),
        line=dict(color='#1E3A8A', width=4),
        marker=dict(
            size=12, 
            color='#1E40AF',
            line=dict(color='white', width=2)
        ),
        text=df_cap["Total Capital%"].apply(lambda x: f'{x:.1%}') if show_data_labels else None,
        textposition='top center',
        textfont=dict(size=11, color='#1E3A8A', family="Inter", weight='bold'),
        hovertemplate="<b>Total CAR</b><br>" +
                     "Period: <b>%{x}</b><br>" +
                     "Ratio: <b>%{y:.2%}</b><br>" +
                     "<extra></extra>"
    ))
    
    # Enhanced regulatory limits with annotations
    fig_cap.add_hline(
        y=Config.MIN_TOTAL_CAPITAL,
        line_dash="dash",
        line_color="#EF4444",
        line_width=2,
        annotation=dict(
            text=f"<b>Min CAR: {Config.MIN_TOTAL_CAPITAL:.1%}</b>",
            font=dict(size=12, color="#EF4444", family="Inter"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#EF4444",
            borderwidth=2,
            borderpad=4
        ),
        annotation_position="left"
    )
    
    fig_cap.add_hline(
        y=Config.MIN_CORE_CAPITAL,
        line_dash="dot",
        line_color="#F59E0B",
        line_width=2,
        annotation=dict(
            text=f"<b>Min Tier 1: {Config.MIN_CORE_CAPITAL:.1%}</b>",
            font=dict(size=12, color="#F59E0B", family="Inter"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#F59E0B",
            borderwidth=2,
            borderpad=4
        ),
        annotation_position="right"
    )
    
    fig_cap.update_layout(
        template="plotly_white",
        yaxis_tickformat=".1%",
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>Capital Ratio</b>",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#E2E8F0",
            borderwidth=2,
            font=dict(size=11, family="Inter")
        ),
        height=chart_height,
        margin=dict(t=40, b=100, l=80, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            title_font=dict(size=13, family="Inter", color="#1E3A8A")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            title_font=dict(size=13, family="Inter", color="#1E3A8A")
        )
    )
    
    st.plotly_chart(fig_cap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Capital Position Summary
    st.markdown("#### 💰 Current Capital Position")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        core_cap_delta = current_core_cap - prev_core_cap
        st.metric(
            "Tier 1 Capital",
            f"{current_core_cap:.2%}",
            delta=f"{core_cap_delta:+.2%}"
        )
    
    with col2:
        total_cap_delta = current_total_cap - prev_total_cap
        st.metric(
            "Total CAR",
            f"{current_total_cap:.2%}",
            delta=f"{total_cap_delta:+.2%}"
        )
    
    with col3:
        buffer = current_total_cap - Config.MIN_TOTAL_CAPITAL
        st.metric(
            "Capital Buffer",
            f"{buffer:.2%}",
            delta="Compliant" if buffer > 0 else "Non-Compliant",
            delta_color="normal" if buffer > 0 else "inverse"
        )
    
    with col4:
        tier2_capital = current_total_cap - current_core_cap
        st.metric(
            "Tier 2 Capital",
            f"{tier2_capital:.2%}",
            delta="Supplementary"
        )
    
    # Regulatory Compliance Checklist with enhanced styling
    st.markdown("#### ✅ Regulatory Compliance Checklist")
    
    compliance_checks = [
        {
            "Requirement": "Minimum Total CAR",
            "Threshold": f"{Config.MIN_TOTAL_CAPITAL:.1%}",
            "Current": f"{current_total_cap:.2%}",
            "Status": "✅ Compliant" if current_total_cap >= Config.MIN_TOTAL_CAPITAL else "❌ Non-Compliant",
            "Gap": f"{(current_total_cap - Config.MIN_TOTAL_CAPITAL):.2%}"
        },
        {
            "Requirement": "Minimum Tier 1 Capital",
            "Threshold": f"{Config.MIN_CORE_CAPITAL:.1%}",
            "Current": f"{current_core_cap:.2%}",
            "Status": "✅ Compliant" if current_core_cap >= Config.MIN_CORE_CAPITAL else "❌ Non-Compliant",
            "Gap": f"{(current_core_cap - Config.MIN_CORE_CAPITAL):.2%}"
        },
        {
            "Requirement": "Gross NPA Target",
            "Threshold": f"{Config.TARGET_GNPA:.1%}",
            "Current": f"{current_gnpa:.2%}",
            "Status": "✅ Within Target" if current_gnpa <= Config.TARGET_GNPA else "⚠️ Needs Attention",
            "Gap": f"{(current_gnpa - Config.TARGET_GNPA):.2%}"
        }
    ]
    
    compliance_df = pd.DataFrame(compliance_checks)
    st.dataframe(compliance_df, use_container_width=True, hide_index=True)

# ---------------------- Tab 4: Executive Summary ----------------------
with tab4:
    st.markdown("### 📑 Executive Summary Report")
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                    padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem;
                    border-left: 4px solid #3B82F6;'>
            <strong style='color: #1E3A8A;'>Period:</strong> {selected_month} | 
            <strong style='color: #1E3A8A;'>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    """, unsafe_allow_html=True)
    
    # Key Highlights
    st.markdown("#### 🎯 Key Highlights")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.markdown("##### 📊 Performance Metrics")
        
        perf_summary = f"""
        - **Gross NPA:** {current_gnpa:.2%} ({'+' if current_gnpa > prev_gnpa else ''}{(current_gnpa - prev_gnpa):.2%} vs Previous)
        - **Net NPA:** {current_nnpa:.2%} ({'+' if current_nnpa > prev_nnpa else ''}{(current_nnpa - prev_nnpa):.2%} vs Previous)
        - **Provision Coverage:** {provision_coverage:.1%}
        - **Status:** {'⚠️ Above target' if current_gnpa > Config.TARGET_GNPA else '✅ Within target'}
        """
        st.markdown(perf_summary)
    
    with summary_col2:
        st.markdown("##### 🛡️ Capital Position")
        
        capital_summary = f"""
        - **Total CAR:** {current_total_cap:.2%} ({'+' if current_total_cap > prev_total_cap else ''}{(current_total_cap - prev_total_cap):.2%} vs Previous)
        - **Tier 1 Capital:** {current_core_cap:.2%}
        - **Capital Buffer:** {buffer:.2%}
        - **Compliance:** {'✅ Regulatory compliant' if buffer > 0 else '❌ Below minimum'}
        """
        st.markdown(capital_summary)
    
    st.markdown("---")
    
    # Risk Assessment
    st.markdown("#### ⚠️ Risk Assessment")
    
    risk_level = 0
    risk_factors = []
    
    if current_gnpa > Config.TARGET_GNPA * 1.5:
        risk_level += 2
        risk_factors.append("🔴 **Critical:** Gross NPA significantly above target")
    elif current_gnpa > Config.TARGET_GNPA:
        risk_level += 1
        risk_factors.append("🟡 **Moderate:** Gross NPA above target threshold")
    
    if current_total_cap < Config.MIN_TOTAL_CAPITAL:
        risk_level += 2
        risk_factors.append("🔴 **Critical:** Capital adequacy below regulatory minimum")
    elif current_total_cap < Config.MIN_TOTAL_CAPITAL * 1.1:
        risk_level += 1
        risk_factors.append("🟡 **Moderate:** Capital buffer is thin")
    
    if (current_gnpa - prev_gnpa) > 0.005:
        risk_level += 1
        risk_factors.append("🟡 **Watch:** Significant NPA deterioration period-over-period")
    
    if risk_level == 0:
        st.success("✅ **Overall Risk Level: LOW** - All key metrics within acceptable parameters")
    elif risk_level <= 2:
        st.warning("⚠️ **Overall Risk Level: MODERATE** - Some metrics require attention")
        for factor in risk_factors:
            st.markdown(f"- {factor}")
    else:
        st.error("🚨 **Overall Risk Level: HIGH** - Immediate management intervention required")
        for factor in risk_factors:
            st.markdown(f"- {factor}")
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("#### 💡 Strategic Recommendations")
    
    recommendations = []
    
    if current_gnpa > Config.TARGET_GNPA:
        recommendations.append({
            "Area": "Asset Quality",
            "Recommendation": "Implement enhanced credit monitoring and recovery mechanisms",
            "Priority": "High",
            "Timeline": "Immediate"
        })
    
    if buffer < 0.02:
        recommendations.append({
            "Area": "Capital Management",
            "Recommendation": "Explore capital raising options (equity, subordinated debt)",
            "Priority": "High" if buffer < 0 else "Medium",
            "Timeline": "30-60 days"
        })
    
    if (current_gnpa - prev_gnpa) > 0:
        recommendations.append({
            "Area": "Risk Management",
            "Recommendation": "Review underwriting standards and strengthen loan appraisal process",
            "Priority": "Medium",
            "Timeline": "60-90 days"
        })
    
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No immediate action items - Continue monitoring key metrics")
    
    st.markdown("---")
    
    # Download Section
    st.markdown("#### 📥 Export Options")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📊 Download Full Report", use_container_width=True):
            st.info("📝 Full report download will be available in the next release")
    
    with export_col2:
        if st.button("📈 Export Charts", use_container_width=True):
            st.info("📊 Chart export feature coming soon")
    
    with export_col3:
        if st.button("📧 Email Report", use_container_width=True):
            st.info("✉️ Email integration will be available in the next release")

# ---------------------- Enhanced Footer ----------------------
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])

with footer_col1:
    st.caption(f"""
        🔒 **Confidential MIS Report** | Basel Analytics Platform v{Config.VERSION}  
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')} | FY {Config.FISCAL_YEAR}
    """)

with footer_col2:
    st.caption("**Data Refresh:** Every hour | **Status:** 🟢 Active")

with footer_col3:
    if st.button("🔄 Refresh Data", key="refresh_footer", help="Reload data from server"):
        st.cache_data.clear()
        st.rerun()
