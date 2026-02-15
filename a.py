import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
import requests
import numpy as np

# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="Executive MIS | Financial Analytics",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Professional Theme & CSS ----------------------
st.markdown("""
<style>
    /* Corporate Palette */
    :root {
        --primary-blue: #1E3A8A;
        --soft-bg: #F8FAFC;
    }
    
    .main { background-color: var(--soft-bg); }
    
    /* MIS KPI Cards */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #1E3A8A;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-label { font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 2rem; font-weight: 800; color: #0F172A; margin: 0.3rem 0; }
    
    /* Navigation override */
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Access Layer ----------------------
@st.cache_data(ttl=3600)
def load_mis_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        
        # Sheet Parsing
        df_main = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
        df_npa = xls.parse("Sheet1")
        df_cap = xls.parse("capital")
        
        return df_main, df_npa, df_cap
    except Exception as e:
        st.error(f"⚠️ Critical Data Link Failure: {e}")
        return None, None, None

df_main, df_npa, df_cap = load_mis_data()

if df_main is None:
    st.stop()

# ---------------------- Sidebar Controls ----------------------
with st.sidebar:
    st.markdown("### 🛠️ MIS ADMINISTRATION")
    all_months = df_main["Month"].unique().tolist()
    selected_month = st.selectbox("Select Reporting Cycle", options=all_months, index=len(all_months)-1)
    
    st.markdown("---")
    st.markdown("### 📥 REPORT GENERATION")
    st.download_button("Export Monthly PDF", data="Placeholder", file_name="Report.pdf", disabled=True)
    st.caption("Reporting Engine: v2.4.1")

# ---------------------- Header ----------------------
c1, c2 = st.columns([3, 1])
with c1:
    st.title("Financial Risk & Capital Intelligence")
    st.caption(f"Status: Audited Data | Reporting Period: {selected_month}")

# ---------------------- KPI Calculations ----------------------
# Identify index for latest and previous month based on selection
try:
    current_idx = df_npa[df_npa['Month'] == selected_month].index[0]
    prev_idx = max(0, current_idx - 1)
except IndexError:
    current_idx, prev_idx = 0, 0

def draw_kpi(label, current_val, prev_val, is_percentage=True, lower_is_better=False):
    delta = (current_val - prev_val)
    if is_percentage:
        display_val = f"{current_val:.2%}"
        delta_val = f"{delta*100:+.2f}%"
    else:
        display_val = f"{current_val:,.0f}"
        delta_val = f"{delta:+,.0f}"
    
    # Determine color for Delta
    if lower_is_better:
        color = "#EF4444" if delta > 0 else "#10B981"
    else:
        color = "#10B981" if delta > 0 else "#EF4444"

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{display_val}</div>
            <div style="color: {color}; font-size: 0.9rem; font-weight: bold;">
                {delta_val} <span style="color: #94A3B8; font-weight: normal;">vs Prev</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Executive Summary Row ----------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    draw_kpi("Gross NPA", df_npa.loc[current_idx, "Gross Npa To Gross Advances"], df_npa.loc[prev_idx, "Gross Npa To Gross Advances"], lower_is_better=True)
with k2:
    draw_kpi("Net NPA", df_npa.loc[current_idx, "Net Npa To Net Advances"], df_npa.loc[prev_idx, "Net Npa To Net Advances"], lower_is_better=True)
with k3:
    draw_kpi("Tier I Capital", df_cap.loc[current_idx, "Core Capital%"], df_cap.loc[prev_idx, "Core Capital%"])
with k4:
    draw_kpi("Total Capital (CAR)", df_cap.loc[current_idx, "Total Capital%"], df_cap.loc[prev_idx, "Total Capital%"])

# ---------------------- Content Tabs ----------------------
tab_analytics, tab_risk, tab_compliance = st.tabs(["📊 Financial Performance", "🔍 Risk Analysis", "🛡️ Regulatory Compliance"])

with tab_analytics:
    st.subheader("Statement of Financial Particulars")
    col_table, col_chart = st.columns([1, 2])
    
    with col_table:
        m_data = df_main[df_main["Month"] == selected_month][["Particulars", "Rs"]]
        st.dataframe(m_data, use_container_width=True, hide_index=True, height=400)
        
    with col_chart:
        options = st.multiselect("Metric Drill-down", options=df_main["Particulars"].unique(), default=df_main["Particulars"].unique()[:2])
        filtered_trend = df_main[df_main["Particulars"].isin(options)]
        fig = px.line(filtered_trend, x="Month", y="Rs", color="Particulars", template="plotly_white", markers=True)
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

with tab_risk:
    st.subheader("Asset Quality Monitoring")
    st.info("The Credit Risk Matrix provides a standardized approach to assessing the creditworthiness of various asset classes.")
    
    # Image replacement (Domain-specific diagram)
    

[Image of credit risk assessment matrix]

    
    fig_npa = go.Figure()
    fig_npa.add_trace(go.Bar(x=df_npa["Month"], y=df_npa["Gross Npa To Gross Advances"], name="Gross NPA", marker_color='#1E3A8A'))
    fig_npa.add_trace(go.Scatter(x=df_npa["Month"], y=df_npa["Net Npa To Net Advances"], name="Net NPA", line=dict(color='#EF4444', width=3)))
    fig_npa.update_layout(yaxis_tickformat=".2%", template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig_npa, use_container_width=True)

with tab_compliance:
    st.subheader("Capital Adequacy (Basel III)")
    
    with st.expander("ℹ️ Regulatory Requirements Overview"):
        st.markdown("""
        Under Basel III, the bank must maintain specific capital buffers:
        * **Common Equity Tier 1:** 4.5% 
        * **Tier 1 Capital:** 6.0%
        * **Total Capital Ratio (CAR):** 8.0% + Capital Conservation Buffer
        """)
        

    fig_cap = px.area(df_cap, x="Month", y=["Core Capital%", "Total Capital%"], 
                      color_discrete_map={"Core Capital%": "#93C5FD", "Total Capital%": "#1E3A8A"},
                      template="plotly_white")
    # Regulatory minimum threshold line
    fig_cap.add_hline(y=0.085, line_dash="dash", line_color="red", annotation_text="Minimum CAR Threshold (8.5%)")
    fig_cap.update_layout(yaxis_tickformat=".1%", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_cap, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #94A3B8; font-size: 0.8rem; padding-bottom: 20px;">
        CONFIDENTIAL | Internal MIS Engine | System Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
""", unsafe_allow_html=True)
