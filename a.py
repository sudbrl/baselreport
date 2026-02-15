import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
import requests

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
    :root {
        --primary-blue: #1E3A8A;
        --soft-bg: #F8FAFC;
    }
    .main { background-color: var(--soft-bg); }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #1E3A8A;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-label { font-size: 0.8rem; color: #64748B; font-weight: 700; text-transform: uppercase; }
    .metric-value { font-size: 2rem; font-weight: 800; color: #0F172A; margin: 0.3rem 0; }
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
    st.caption("Reporting Engine: v2.4.1")

# ---------------------- Header ----------------------
st.title("Financial Risk & Capital Intelligence")
st.caption(f"Status: Audited Data | Reporting Period: {selected_month}")

# ---------------------- KPI Logic ----------------------
try:
    current_idx = df_npa[df_npa['Month'] == selected_month].index[0]
    prev_idx = max(0, current_idx - 1)
except:
    current_idx, prev_idx = 0, 0

def draw_kpi(label, current_val, prev_val, lower_is_better=False):
    delta = (current_val - prev_val)
    color = "#EF4444" if (delta > 0 and lower_is_better) or (delta < 0 and not lower_is_better) else "#10B981"
    arrow = "▲" if delta > 0 else "▼"
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{current_val:.2%}</div>
            <div style="color: {color}; font-size: 0.9rem; font-weight: bold;">
                {arrow} {abs(delta)*100:.2f}% <span style="color: #94A3B8; font-weight: normal;">vs Last Period</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Executive Summary Row ----------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    draw_kpi("Gross NPA", df_npa.loc[current_idx, "Gross Npa To Gross Advances"], df_npa.loc[prev_idx, "Gross Npa To Gross Advances"], True)
with k2:
    draw_kpi("Net NPA", df_npa.loc[current_idx, "Net Npa To Net Advances"], df_npa.loc[prev_idx, "Net Npa To Net Advances"], True)
with k3:
    draw_kpi("Tier I Capital", df_cap.loc[current_idx, "Core Capital%"], df_cap.loc[prev_idx, "Core Capital%"])
with k4:
    draw_kpi("Capital Adequacy", df_cap.loc[current_idx, "Total Capital%"], df_cap.loc[prev_idx, "Total Capital%"])

st.markdown("---")

# ---------------------- Main Content ----------------------
tabs = st.tabs(["📊 Performance", "🔍 Risk Analysis", "🛡️ Regulatory"])

with tabs[0]:
    st.subheader("Particulars Drill-down")
    options = st.multiselect("Select Metrics", options=df_main["Particulars"].unique(), default=df_main["Particulars"].unique()[:2])
    filtered = df_main[df_main["Particulars"].isin(options)]
    fig = px.line(filtered, x="Month", y="Rs", color="Particulars", template="plotly_white", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Asset Quality (NPA) Trend")
    st.info("💡 **MIS Note:** A narrowing gap between Gross and Net NPA indicates high provisioning coverage.")
    
    # Chart
    fig_npa = go.Figure()
    fig_npa.add_trace(go.Bar(x=df_npa["Month"], y=df_npa["Gross Npa To Gross Advances"], name="Gross NPA", marker_color='#1E3A8A'))
    fig_npa.add_trace(go.Scatter(x=df_npa["Month"], y=df_npa["Net Npa To Net Advances"], name="Net NPA", line=dict(color='#EF4444', width=3)))
    fig_npa.update_layout(yaxis_tickformat=".2%", template="plotly_white")
    st.plotly_chart(fig_npa, use_container_width=True)

with tabs[2]:
    st.subheader("Capital Ratios vs Regulatory Minimums")
    
    # Replace the error with an expander for information
    with st.expander("📖 Basel III Framework Reference"):
        st.write("The following metrics represent the bank's ability to absorb losses and meet regulatory Tier 1 and Tier 2 requirements.")
    
    fig_cap = px.area(df_cap, x="Month", y=["Core Capital%", "Total Capital%"], 
                      color_discrete_map={"Core Capital%": "#93C5FD", "Total Capital%": "#1E3A8A"},
                      template="plotly_white")
    fig_cap.add_hline(y=0.085, line_dash="dash", line_color="red", annotation_text="Minimum CAR (8.5%)")
    fig_cap.update_layout(yaxis_tickformat=".1%")
    st.plotly_chart(fig_cap, use_container_width=True)

# ---------------------- Footer ----------------------
st.markdown(f"<div style='text-align: center; color: #94A3B8; font-size: 0.8rem;'>Internal MIS | {datetime.now().strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)
