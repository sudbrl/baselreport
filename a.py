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
    section[data-testid="stSidebar"] { background-color: #0F172A !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Access Layer ----------------------
@st.cache_data(ttl=3600)
def load_mis_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        
        df = xls.parse("Data")
        
        # ── Normalize all column names ──────────────────────────────────────
        # Strip whitespace, collapse internal spaces, fix encoding issues
        df.columns = (
            df.columns
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.replace('\xa0', ' ')   # non-breaking space
        )
        
        # Drop helper / unnamed columns
        drop_candidates = [c for c in df.columns if
                           c.startswith("Unnamed") or c in ("Helper", "Rs.1", "Rs.2", "Movements(%)")]
        df.drop(columns=drop_candidates, errors="ignore", inplace=True)
        
        return df

    except Exception as e:
        st.error(f"MIS Connection Failure: {e}")
        return None

# ---------------------- Column Discovery Utility ----------------------
def find_col(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """
    Case-insensitive search: returns first column whose name contains
    ALL keywords provided (as substrings).
    """
    for col in df.columns:
        col_lower = col.lower()
        if all(kw.lower() in col_lower for kw in keywords):
            return col
    return None

# ---------------------- Load Data ----------------------
df = load_mis_data()

if df is None:
    st.stop()

# ── Debug expander (remove in production if desired) ─────────────────────────
with st.sidebar.expander("🔧 Column Inspector"):
    st.write("**All columns detected:**")
    st.write(list(df.columns))

# ---------------------- Resolve Critical Columns ----------------------
COL_MONTH        = find_col(df, ["month"])
COL_PARTICULARS  = find_col(df, ["particular"])
COL_RS           = find_col(df, ["rs"])          # main value column
COL_GROSS_NPA    = find_col(df, ["gross", "npa", "advance"])
COL_NET_NPA      = find_col(df, ["net", "npa",  "advance"])
COL_CORE_CAP     = find_col(df, ["core", "capital"])
COL_TOTAL_CAP    = find_col(df, ["total", "capital"])

# Report any missing critical columns
missing = {
    "Month":         COL_MONTH,
    "Particulars":   COL_PARTICULARS,
    "Rs":            COL_RS,
    "Gross NPA":     COL_GROSS_NPA,
    "Net NPA":       COL_NET_NPA,
    "Core Capital":  COL_CORE_CAP,
    "Total Capital": COL_TOTAL_CAP,
}

unresolved = [k for k, v in missing.items() if v is None]
if unresolved:
    st.error(
        f"Could not auto-detect columns for: **{', '.join(unresolved)}**\n\n"
        f"Available columns: `{list(df.columns)}`\n\n"
        "Please check the **Column Inspector** in the sidebar and update keyword hints."
    )
    st.stop()

# Friendly aliases
df_main = df.rename(columns={
    COL_MONTH:       "Month",
    COL_PARTICULARS: "Particulars",
    COL_RS:          "Rs",
})
df_npa  = df_main.copy()
df_cap  = df_main.copy()

# ---------------------- Sidebar Filters ----------------------
with st.sidebar:
    st.title("MIS CONTROLS")
    st.markdown("---")
    st.caption("🔍 REPORT DRILL-DOWN")

    all_months = df_main["Month"].dropna().unique().tolist()
    selected_month = st.selectbox("Cycle", options=all_months, index=len(all_months) - 1)

    available_parts = df_main["Particulars"].dropna().unique().tolist()
    selected_parts  = st.multiselect(
        "Metrics",
        options=available_parts,
        default=available_parts[:2] if len(available_parts) >= 2 else available_parts
    )

    st.markdown("---")
    st.caption("Engine: v3.3 | Financial Year 2025-26")

# ---------------------- Index Helpers ----------------------
def get_indices(col_month, month_val):
    """Return (current_idx, prev_idx) for a given month value."""
    mask = df_main[col_month] == month_val
    if not mask.any():
        return 0, 0
    c = df_main.index[mask][0]
    p = max(df_main.index[0], c - 1)
    return c, p

c_idx, p_idx = get_indices("Month", selected_month)

# ---------------------- KPI Card ----------------------
def draw_kpi(label: str, current: float, prev: float, lower_better: bool = False):
    delta = current - prev
    improving = (delta < 0 and lower_better) or (delta > 0 and not lower_better)
    color  = "#10B981" if improving else "#EF4444"
    arrow  = "▲" if delta > 0 else "▼"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{current:.2%}</div>
            <div style="color:{color}; font-size:0.85rem; font-weight:bold;">
                {arrow} {abs(delta)*100:.2f}%
                <span style="color:#94A3B8; font-weight:normal;"> vs LP</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Header & KPIs ----------------------
st.title("Financial Risk Intelligence")

k1, k2, k3, k4 = st.columns(4)
with k1:
    draw_kpi("Gross NPA",
             df_main.loc[c_idx, COL_GROSS_NPA],
             df_main.loc[p_idx, COL_GROSS_NPA],
             lower_better=True)
with k2:
    draw_kpi("Net NPA",
             df_main.loc[c_idx, COL_NET_NPA],
             df_main.loc[p_idx, COL_NET_NPA],
             lower_better=True)
with k3:
    draw_kpi("Core Capital",
             df_main.loc[c_idx, COL_CORE_CAP],
             df_main.loc[p_idx, COL_CORE_CAP])
with k4:
    draw_kpi("Capital Adequacy",
             df_main.loc[c_idx, COL_TOTAL_CAP],
             df_main.loc[p_idx, COL_TOTAL_CAP])

st.markdown("---")

# ---------------------- Tabs ----------------------
tab1, tab2, tab3 = st.tabs(["📊 Performance Trend", "📉 Asset Quality", "🛡️ Compliance"])

# ── Tab 1 : Performance Trend ──────────────────────────────────────────────
with tab1:
    st.subheader("Financial Performance Drill-down")

    if not selected_parts:
        st.warning("Select at least one metric from the sidebar.")
    else:
        trend_df = df_main[df_main["Particulars"].isin(selected_parts)]
        fig1 = px.line(
            trend_df, x="Month", y="Rs", color="Particulars",
            markers=True, template="plotly_white"
        )
        fig1.update_traces(
            mode="lines+markers+text",
            texttemplate="%{y:.3s}",
            textposition="top center"
        )
        fig1.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig1, use_container_width=True)

# ── Tab 2 : Asset Quality ──────────────────────────────────────────────────
with tab2:
    st.subheader("Asset Quality Monitoring")
    st.info("Credit Risk Assessment Matrix — provisioning requirements by loan classification.")

    with st.expander("📊 Risk Classification Standards"):
        st.markdown("""
        | Category | Definition | Provisioning |
        |---|---|---|
        | **Standard** | Timely repayment | 0.25% – 2% |
        | **Sub-Standard** | Overdue > 90 days | 15% – 25% |
        | **Doubtful** | Overdue > 12 months | 25% – 100% |
        | **Loss** | Non-recoverable | 100% |
        *Basel III regulatory guidelines*
        """)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_npa["Month"],
        y=df_npa[COL_GROSS_NPA],
        name="Gross NPA",
        marker_color="#1E3A8A",
        text=df_npa[COL_GROSS_NPA].apply(lambda x: f"{x:.2%}"),
        textposition="outside"
    ))
    fig2.add_trace(go.Scatter(
        x=df_npa["Month"],
        y=df_npa[COL_NET_NPA],
        name="Net NPA",
        mode="lines+markers+text",
        line=dict(color="#EF4444", width=3),
        text=df_npa[COL_NET_NPA].apply(lambda x: f"{x:.2%}"),
        textposition="top center"
    ))
    fig2.update_layout(
        yaxis_tickformat=".2%",
        template="plotly_white",
        xaxis_title="Period",
        yaxis_title="NPA Ratio",
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 3 : Compliance ─────────────────────────────────────────────────────
with tab3:
    st.subheader("Capital Adequacy & Buffer Analysis")
    st.info("Basel III: Tier 1 & Tier 2 capital must remain above regulatory minimums.")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_cap["Month"], y=df_cap[COL_CORE_CAP],
        name="Core Capital",
        fill="tozeroy", mode="lines+markers+text",
        line=dict(color="#93C5FD"),
        text=df_cap[COL_CORE_CAP].apply(lambda x: f"{x:.1%}"),
        textposition="top center"
    ))
    fig3.add_trace(go.Scatter(
        x=df_cap["Month"], y=df_cap[COL_TOTAL_CAP],
        name="Total Capital",
        fill="tonexty", mode="lines+markers+text",
        line=dict(color="#1E3A8A"),
        text=df_cap[COL_TOTAL_CAP].apply(lambda x: f"{x:.1%}"),
        textposition="top center"
    ))
    fig3.add_hline(
        y=0.085, line_dash="dash", line_color="red",
        annotation_text="Regulatory Floor (8.5%)"
    )
    fig3.update_layout(
        yaxis_tickformat=".1%",
        legend=dict(orientation="h", y=1.1),
        xaxis_title="Period",
        yaxis_title="Capital Ratio",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Current Capital Position")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            "Core Capital",
            f"{df_cap.loc[c_idx, COL_CORE_CAP]:.2%}",
            delta=f"{df_cap.loc[c_idx, COL_CORE_CAP] - df_cap.loc[p_idx, COL_CORE_CAP]:.2%}"
        )
    with c2:
        st.metric(
            "Total Capital",
            f"{df_cap.loc[c_idx, COL_TOTAL_CAP]:.2%}",
            delta=f"{df_cap.loc[c_idx, COL_TOTAL_CAP] - df_cap.loc[p_idx, COL_TOTAL_CAP]:.2%}"
        )
    with c3:
        buffer = df_cap.loc[c_idx, COL_TOTAL_CAP] - 0.085
        st.metric(
            "Capital Buffer",
            f"{buffer:.2%}",
            delta="Above minimum" if buffer > 0 else "Below minimum",
            delta_color="normal" if buffer > 0 else "inverse"
        )

st.markdown("---")
st.caption(f"Confidential MIS Report | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
