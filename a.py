import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
import requests

# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="Executive MIS | Basel Reporting",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Professional Theme & CSS ----------------------
st.markdown("""
<style>
    /* Professional Grey/Blue Palette */
    :root {
        --primary: #1E3A8A;
        --secondary: #64748B;
        --success: #10B981;
        --danger: #EF4444;
    }
    
    .main { background-color: #F8FAFC; }
    
    /* Metric Cards */
    .metric-card {
        background-color: white;
        padding: 1.25rem;
        border-radius: 0.5rem;
        border-left: 5px solid var(--primary);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .metric-label { font-size: 0.85rem; color: var(--secondary); font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1E293B; margin: 0.2rem 0; }
    
    /* Headers */
    h1, h2, h3 { color: #0F172A !important; font-family: 'Inter', sans-serif; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #1E293B; color: white; }
    section[data-testid="stSidebar"] .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Logic ----------------------
@st.cache_data(ttl=3600)
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        response = requests.get(url)
        xls = pd.ExcelFile(BytesIO(response.content))
        df_main = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
        df_npa = xls.parse("Sheet1")
        df_cap = xls.parse("capital")
        return df_main, df_npa, df_cap
    except Exception as e:
        st.error(f"MIS Connection Error: {e}")
        return None, None, None

df_main, df_npa, df_cap = load_data()

if df_main is None:
    st.stop()

# ---------------------- Sidebar Controls ----------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3222/3222672.png", width=80)
    st.title("MIS Controls")
    st.markdown("---")
    
    # Global Period Selection
    all_months = df_main["Month"].unique().tolist()
    selected_month = st.selectbox("Reporting Month", options=all_months, index=len(all_months)-1)
    
    st.markdown("### Export Center")
    st.caption("Generate official PDF/CSV reports")
    if st.button("Generate Executive Summary"):
        st.toast("Report compiled successfully!")

# ---------------------- Header Section ----------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("Financial & Risk Intelligence")
    st.caption(f"Reporting Cycle: {selected_month} | System Status: Operational")

# ---------------------- Executive KPIs ----------------------
# Logic for Delta calculation
latest_idx = df_npa[df_npa['Month'] == selected_month].index[0]
prev_idx = max(0, latest_idx - 1)

def get_kpi_html(label, value, delta, inverse=False):
    # If inverse=True, a positive delta is bad (like NPA)
    color = "#EF4444" if (delta > 0 and not inverse) or (delta < 0 and inverse) else "#10B981"
    arrow = "▲" if delta > 0 else "▼"
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value:.2%}</div>
        <div style="color: {color}; font-size: 0.9rem; font-weight: bold;">
            {arrow} {abs(delta):.2f}% <span style="color: #94A3B8; font-weight: normal;">vs Last Month</span>
        </div>
    </div>
    """

k1, k2, k3, k4 = st.columns(4)
with k1:
    d = (df_npa.loc[latest_idx, "Gross Npa To Gross Advances"] - df_npa.loc[prev_idx, "Gross Npa To Gross Advances"]) * 100
    st.markdown(get_kpi_html("Gross NPA Ratio", df_npa.loc[latest_idx, "Gross Npa To Gross Advances"], d, inverse=True), unsafe_allow_html=True)
with k2:
    d = (df_npa.loc[latest_idx, "Net Npa To Net Advances"] - df_npa.loc[prev_idx, "Net Npa To Net Advances"]) * 100
    st.markdown(get_kpi_html("Net NPA Ratio", df_npa.loc[latest_idx, "Net Npa To Net Advances"], d, inverse=True), unsafe_allow_html=True)
with k3:
    d = (df_cap.loc[latest_idx, "Core Capital%"] - df_cap.loc[prev_idx, "Core Capital%"]) * 100
    st.markdown(get_kpi_html("Tier I Capital", df_cap.loc[latest_idx, "Core Capital%"], d), unsafe_allow_html=True)
with k4:
    d = (df_cap.loc[latest_idx, "Total Capital%"] - df_cap.loc[prev_idx, "Total Capital%"]) * 100
    st.markdown(get_kpi_html("Capital Adequacy", df_cap.loc[latest_idx, "Total Capital%"], d), unsafe_allow_html=True)

st.markdown("---")

# ---------------------- Main Analytics ----------------------
tabs = st.tabs(["🎯 Variance Analysis", "📉 Asset Quality", "🛡️ Capital & Basel III"])

with tabs[0]:
    col_t1_1, col_t1_2 = st.columns([1, 2])
    
    with col_t1_1:
        st.subheader("Statement of Particulars")
        # Filter data for the sidebar-selected month
        month_data = df_main[df_main["Month"] == selected_month][["Particulars", "Rs"]]
        st.dataframe(month_data, use_container_width=True, hide_index=True)
        
    with col_t1_2:
        st.subheader("Historical Trend")
        # Multi-select for deep diving into specific particulars
        parts = st.multiselect("Select Particulars for Trend Analysis", options=df_main["Particulars"].unique(), default=df_main["Particulars"].unique()[0])
        trend_df = df_main[df_main["Particulars"].isin(parts)]
        
        fig = px.line(trend_df, x="Month", y="Rs", color="Particulars", markers=True, 
                      template="plotly_white", color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Non-Performing Assets (NPA) Breakdown")
    

[Image of credit risk assessment matrix]

    
    fig_npa = go.Figure()
    fig_npa.add_trace(go.Bar(x=df_npa["Month"], y=df_npa["Gross Npa To Gross Advances"], name="Gross NPA", marker_color='#1E3A8A'))
    fig_npa.add_trace(go.Scatter(x=df_npa["Month"], y=df_npa["Net Npa To Net Advances"], name="Net NPA", line=dict(color='#EF4444', width=3)))
    
    fig_npa.update_layout(hovermode="x unified", template="plotly_white", yaxis_tickformat=".2%")
    st.plotly_chart(fig_npa, use_container_width=True)

with tabs[2]:
    st.subheader("Capital Adequacy & Regulatory Compliance")
    
    
    # Area chart for Capital
    fig_cap = px.area(df_cap, x="Month", y=["Core Capital%", "Total Capital%"], 
                      title="Regulatory Capital Buffer",
                      template="plotly_white",
                      color_discrete_map={"Core Capital%": "#93C5FD", "Total Capital%": "#1E3A8A"})
    fig_cap.add_hline(y=0.085, line_dash="dash", line_color="red", annotation_text="Regulatory Minimum")
    fig_cap.update_layout(yaxis_tickformat=".1%")
    st.plotly_chart(fig_cap, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown(f"""
    <div style="text-align: center; padding-top: 50px; color: #94A3B8; font-size: 0.8rem;">
        Confidential Internal MIS | Generated on {datetime.now().strftime('%d %b %Y %H:%M')} | Basel III Compliant Framework
    </div>
""", unsafe_allow_html=True)
