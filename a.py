import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# ---------------------- Professional Theme & CSS ----------------------
st.markdown("""
<style>
    :root { --primary: #1E3A8A; --bg: #F8FAFC; }
    .main { background-color: var(--bg); }
    
    /* KPI Card Styling */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-top: 4px solid var(--primary);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .metric-label { font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #0F172A; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #0F172A !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    
    /* Adjusting selectbox height for small/modern look */
    .stSelectbox, .stMultiSelect { margin-bottom: -15px; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Access Layer ----------------------
@st.cache_data(ttl=3600)
def load_mis_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        response = requests.get(url)
        xls = pd.ExcelFile(BytesIO(response.content))
        df_main = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
        df_npa = xls.parse("Sheet1")
        df_cap = xls.parse("capital")
        return df_main, df_npa, df_cap
    except Exception as e:
        st.error(f"MIS Connection Failure: {e}")
        return None, None, None

df_main, df_npa, df_cap = load_mis_data()

if df_main is None: st.stop()

# ---------------------- Sidebar Filters (Modern & Small) ----------------------
with st.sidebar:
    st.title("MIS CONTROLS")
    st.markdown("---")
    
    st.caption("🔍 REPORT DRILL-DOWN")
    all_months = df_main["Month"].unique().tolist()
    selected_month = st.selectbox("Cycle", options=all_months, index=len(all_months)-1)
    
    available_parts = df_main["Particulars"].dropna().unique().tolist()
    selected_parts = st.multiselect("Metrics", options=available_parts, default=available_parts[:2])
    
    st.markdown("---")
    st.caption("Engine: v3.2 | Financial Year 2025-26")

# ---------------------- KPI Calculations ----------------------
try:
    c_idx = df_npa[df_npa['Month'] == selected_month].index[0]
    p_idx = max(0, c_idx - 1)
except:
    c_idx, p_idx = 0, 0

def draw_kpi(label, current, prev, lower_better=False):
    delta = current - prev
    color = "#EF4444" if (delta > 0 and lower_better) or (delta < 0 and not lower_better) else "#10B981"
    arrow = "▲" if delta > 0 else "▼"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{current:.2%}</div>
            <div style="color: {color}; font-size: 0.85rem; font-weight: bold;">
                {arrow} {abs(delta)*100:.2f}% <span style="color: #94A3B8; font-weight: normal;">vs LP</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Header & KPIs ----------------------
st.title("Financial Risk Intelligence")
k1, k2, k3, k4 = st.columns(4)
with k1: draw_kpi("Gross NPA", df_npa.loc[c_idx, "Gross Npa To Gross Advances"], df_npa.loc[p_idx, "Gross Npa To Gross Advances"], True)
with k2: draw_kpi("Net NPA", df_npa.loc[c_idx, "Net Npa To Net Advances"], df_npa.loc[p_idx, "Net Npa To Net Advances"], True)
with k3: draw_kpi("Core Capital", df_cap.loc[c_idx, "Core Capital%"], df_cap.loc[p_idx, "Core Capital%"])
with k4: draw_kpi("Capital Adequacy", df_cap.loc[c_idx, "Total Capital%"], df_cap.loc[p_idx, "Total Capital%"])

st.markdown("---")

# ---------------------- Main Content ----------------------
tab1, tab2, tab3 = st.tabs(["📊 Performance Trend", "📉 Asset Quality", "🛡️ Compliance"])

with tab1:
    st.subheader("Financial Performance Drill-down")
    trend_df = df_main[df_main["Particulars"].isin(selected_parts)]
    fig1 = px.line(trend_df, x="Month", y="Rs", color="Particulars", markers=True, template="plotly_white")
    
    # Enable Data Labels (using .2s for smart millions/thousands formatting)
    fig1.update_traces(textposition="top center", texttemplate="%{y:.3s}")
    fig1.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Asset Quality Monitoring")
    st.info("The Credit Risk Assessment Matrix determines the provisioning requirements based on loan classification.")
    
    # Diagram Placeholder Replacement
    with st.expander("📊 View Risk Classification Standards"):
        st.write("Reference matrix for Standard, Sub-standard, Doubtful, and Loss assets.")
    
    

[Image of credit risk assessment matrix]


    fig2 = go.Figure()
    # Bar Labels enabled
    fig2.add_trace(go.Bar(
        x=df_npa["Month"], 
        y=df_npa["Gross Npa To Gross Advances"], 
        name="Gross NPA", 
        marker_color='#1E3A8A',
        text=df_npa["Gross Npa To Gross Advances"].apply(lambda x: f'{x:.2%}'),
        textposition='outside'
    ))
    # Line Labels enabled
    fig2.add_trace(go.Scatter(
        x=df_npa["Month"], 
        y=df_npa["Net Npa To Net Advances"], 
        name="Net NPA", 
        mode='lines+markers+text',
        line=dict(color='#EF4444', width=3),
        text=df_npa["Net Npa To Net Advances"].apply(lambda x: f'{x:.2%}'),
        textposition='top center'
    ))
    fig2.update_layout(yaxis_tickformat=".2%", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Capital Adequacy & Buffer Analysis")
    st.info("Basel III Capital Framework: Maintaining Tier 1 and Tier 2 capital levels above regulatory minimums.")
    
    

    fig3 = px.area(df_cap, x="Month", y=["Core Capital%", "Total Capital%"], 
                   color_discrete_map={"Core Capital%": "#93C5FD", "Total Capital%": "#1E3A8A"}, template="plotly_white")
    
    # Area labels enabled
    fig3.update_traces(mode="lines+markers+text", texttemplate="%{y:.1%}", textposition="top center")
    fig3.add_hline(y=0.085, line_dash="dash", line_color="red", annotation_text="Regulatory Limit (8.5%)")
    fig3.update_layout(yaxis_tickformat=".1%", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption(f"Confidential MIS Report | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
