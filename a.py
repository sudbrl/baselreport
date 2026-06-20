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
        st.error(f"Data load failed: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# ---------------------- Inspect Unique Particulars ----------------------
# Show in sidebar so we know exact row labels
with st.sidebar:
    st.title("MIS CONTROLS")
    st.markdown("---")

    with st.expander("🔧 Row Label Inspector"):
        st.caption("All unique Particulars (row labels):")
        st.dataframe(
            pd.DataFrame({"Particulars": df["Particulars"].dropna().unique()}),
            use_container_width=True,
            height=200
        )

    st.caption("🔍 REPORT DRILL-DOWN")
    all_months     = df["Month"].dropna().unique().tolist()
    selected_month = st.selectbox("Cycle", options=all_months, index=len(all_months) - 1)

    available_parts = df["Particulars"].dropna().unique().tolist()
    selected_parts  = st.multiselect(
        "Metrics",
        options=available_parts,
        default=available_parts[:2] if len(available_parts) >= 2 else available_parts
    )

    st.markdown("---")
    st.caption("Engine: v3.4 | Financial Year 2025-26")

# ---------------------- Row-based Lookup Utility ----------------------
def find_particular(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """
    Searches Particulars column for a row whose label contains
    ALL keywords (case-insensitive). Returns matched label or None.
    """
    for val in df["Particulars"].dropna().unique():
        val_lower = str(val).lower()
        if all(kw.lower() in val_lower for kw in keywords):
            return val
    return None

# ── Auto-detect row labels for KPI metrics ──────────────────────────────────
LABEL_GROSS_NPA  = find_particular(df, ["gross", "npa"])
LABEL_NET_NPA    = find_particular(df, ["net",   "npa"])
LABEL_CORE_CAP   = find_particular(df, ["core",  "capital"])
LABEL_TOTAL_CAP  = find_particular(df, ["total", "capital"])

# Report unresolved labels clearly
labels_check = {
    "Gross NPA":     LABEL_GROSS_NPA,
    "Net NPA":       LABEL_NET_NPA,
    "Core Capital":  LABEL_CORE_CAP,
    "Total Capital": LABEL_TOTAL_CAP,
}
unresolved = [k for k, v in labels_check.items() if v is None]

if unresolved:
    st.error(
        f"⚠️ Could not find row labels for: **{', '.join(unresolved)}**\n\n"
        "Check the **🔧 Row Label Inspector** in the sidebar to see exact labels, "
        "then update the keyword hints in `find_particular()`."
    )
    # Show full unique particulars for debugging
    with st.expander("📋 All Particulars (debug view)"):
        st.dataframe(df[["Particulars"]].drop_duplicates().reset_index(drop=True))
    st.stop()

# ── Confirm detected labels ──────────────────────────────────────────────────
with st.sidebar.expander("✅ Detected KPI Labels"):
    for k, v in labels_check.items():
        st.caption(f"**{k}:** `{v}`")

# ---------------------- Helper: get Rs value for a metric+month ----------------------
def get_value(particular_label: str, month: str) -> float:
    """Returns the Rs value for a given Particulars label and Month."""
    mask = (df["Particulars"] == particular_label) & (df["Month"] == month)
    result = df.loc[mask, "Rs"]
    if result.empty:
        return 0.0
    return float(result.iloc[0])

def get_prev_month(month: str) -> str:
    """Returns the previous month in the dataset, or same if first."""
    months = df["Month"].dropna().unique().tolist()
    idx    = months.index(month) if month in months else 0
    return months[max(0, idx - 1)]

prev_month = get_prev_month(selected_month)

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

# ---------------------- KPI Card ----------------------
def draw_kpi(label: str, current: float, prev: float, 
             lower_better: bool = False, is_pct: bool = True):
    delta     = current - prev
    improving = (delta < 0 and lower_better) or (delta > 0 and not lower_better)
    color     = "#10B981" if improving else "#EF4444"
    arrow     = "▲" if delta > 0 else "▼"
    fmt       = f"{current:.2%}" if is_pct else f"{current:,.2f}"
    delta_fmt = f"{abs(delta)*100:.2f}%" if is_pct else f"{abs(delta):,.2f}"

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{fmt}</div>
            <div style="color:{color}; font-size:0.85rem; font-weight:bold;">
                {arrow} {delta_fmt}
                <span style="color:#94A3B8; font-weight:normal;"> vs prior period</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- Header & KPIs ----------------------
st.title("Financial Risk Intelligence")
st.caption(f"Reporting Period: **{selected_month}** | Prior Period: **{prev_month}**")

k1, k2, k3, k4 = st.columns(4)
with k1: draw_kpi("Gross NPA",        kpi["gross_npa_c"], kpi["gross_npa_p"], lower_better=True)
with k2: draw_kpi("Net NPA",          kpi["net_npa_c"],   kpi["net_npa_p"],   lower_better=True)
with k3: draw_kpi("Core Capital",     kpi["core_cap_c"],  kpi["core_cap_p"])
with k4: draw_kpi("Capital Adequacy", kpi["total_cap_c"], kpi["total_cap_p"])

st.markdown("---")

# ---------------------- Build time-series for specific metrics ----------------------
def get_series(particular_label: str) -> pd.DataFrame:
    """Returns Month + Rs series for a given Particulars label."""
    return (
        df[df["Particulars"] == particular_label][["Month", "Rs"]]
        .copy()
        .reset_index(drop=True)
    )

npa_gross_series  = get_series(LABEL_GROSS_NPA)
npa_net_series    = get_series(LABEL_NET_NPA)
core_cap_series   = get_series(LABEL_CORE_CAP)
total_cap_series  = get_series(LABEL_TOTAL_CAP)

# ---------------------- Tabs ----------------------
tab1, tab2, tab3 = st.tabs(["📊 Performance Trend", "📉 Asset Quality", "🛡️ Compliance"])

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Financial Performance Drill-down")

    if not selected_parts:
        st.warning("Select at least one metric from the sidebar.")
    else:
        trend_df = df[df["Particulars"].isin(selected_parts)].copy()

        if trend_df.empty:
            st.warning("No data found for selected metrics.")
        else:
            fig1 = px.line(
                trend_df, x="Month", y="Rs", color="Particulars",
                markers=True, template="plotly_white",
                title="Metric Trends Over Time"
            )
            fig1.update_traces(
                mode="lines+markers+text",
                texttemplate="%{y:.3s}",
                textposition="top center"
            )
            fig1.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", y=-0.25),
                xaxis_title="Period",
                yaxis_title="Value (Rs)"
            )
            st.plotly_chart(fig1, use_container_width=True)

        # Raw data table
        with st.expander("📋 View Raw Data"):
            st.dataframe(
                trend_df.pivot_table(index="Month", columns="Particulars", 
                                     values="Rs", aggfunc="first"),
                use_container_width=True
            )

# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Asset Quality Monitoring")
    st.info("Tracking Gross and Net NPA ratios across reporting periods.")

    with st.expander("📊 Risk Classification Standards"):
        st.markdown("""
        | Category | Definition | Provisioning |
        |---|---|---|
        | **Standard**     | Timely repayment         | 0.25% – 2%   |
        | **Sub-Standard** | Overdue > 90 days        | 15% – 25%    |
        | **Doubtful**     | Overdue > 12 months      | 25% – 100%   |
        | **Loss**         | Non-recoverable          | 100%         |
        *Basel III regulatory guidelines*
        """)

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=npa_gross_series["Month"],
        y=npa_gross_series["Rs"],
        name="Gross NPA",
        marker_color="#1E3A8A",
        text=npa_gross_series["Rs"].apply(lambda x: f"{x:.2%}" 
                                           if x < 1 else f"{x:,.2f}"),
        textposition="outside"
    ))

    fig2.add_trace(go.Scatter(
        x=npa_net_series["Month"],
        y=npa_net_series["Rs"],
        name="Net NPA",
        mode="lines+markers+text",
        line=dict(color="#EF4444", width=3),
        text=npa_net_series["Rs"].apply(lambda x: f"{x:.2%}" 
                                         if x < 1 else f"{x:,.2f}"),
        textposition="top center"
    ))

    fig2.update_layout(
        template="plotly_white",
        xaxis_title="Period",
        yaxis_title="NPA Ratio / Value",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Side-by-side NPA table
    with st.expander("📋 NPA Data Table"):
        npa_combined = npa_gross_series.merge(
            npa_net_series, on="Month", suffixes=("_Gross", "_Net")
        )
        npa_combined.columns = ["Month", "Gross NPA", "Net NPA"]
        st.dataframe(npa_combined, use_container_width=True)

# ── Tab 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Capital Adequacy & Buffer Analysis")
    st.info("Basel III: Core and Total Capital must remain above regulatory minimums.")

    # Merge for combined chart
    cap_df = core_cap_series.merge(total_cap_series, on="Month", suffixes=("_Core", "_Total"))
    cap_df.columns = ["Month", "Core Capital", "Total Capital"]

    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=cap_df["Month"], y=cap_df["Core Capital"],
        name="Core Capital",
        fill="tozeroy",
        mode="lines+markers+text",
        line=dict(color="#93C5FD", width=2),
        text=cap_df["Core Capital"].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:,.1f}"),
        textposition="top center"
    ))

    fig3.add_trace(go.Scatter(
        x=cap_df["Month"], y=cap_df["Total Capital"],
        name="Total Capital",
        fill="tonexty",
        mode="lines+markers+text",
        line=dict(color="#1E3A8A", width=2),
        text=cap_df["Total Capital"].apply(lambda x: f"{x:.2%}" if x < 1 else f"{x:,.1f}"),
        textposition="top center"
    ))

    # Regulatory floor — adjust 0.085 if values are stored as 8.5 instead of 0.085
    reg_floor       = 0.085 if cap_df["Total Capital"].max() < 1 else 8.5
    fig3.add_hline(
        y=reg_floor, line_dash="dash", line_color="red",
        annotation_text=f"Regulatory Floor ({reg_floor:.1%})" 
                         if reg_floor < 1 else f"Regulatory Floor ({reg_floor}%)"
    )

    fig3.update_layout(
        template="plotly_white",
        xaxis_title="Period",
        yaxis_title="Capital Ratio",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Capital metrics
    st.markdown("#### Current Capital Position")
    c1, c2, c3 = st.columns(3)

    core_fmt  = f"{kpi['core_cap_c']:.2%}"  if kpi["core_cap_c"]  < 1 else f"{kpi['core_cap_c']:.2f}%"
    total_fmt = f"{kpi['total_cap_c']:.2%}" if kpi["total_cap_c"] < 1 else f"{kpi['total_cap_c']:.2f}%"

    with c1:
        st.metric("Core Capital",  core_fmt,
                  delta=f"{kpi['core_cap_c']  - kpi['core_cap_p']:.4f}")
    with c2:
        st.metric("Total Capital", total_fmt,
                  delta=f"{kpi['total_cap_c'] - kpi['total_cap_p']:.4f}")
    with c3:
        buffer = kpi["total_cap_c"] - reg_floor
        st.metric(
            "Capital Buffer",
            f"{buffer:.2%}" if abs(buffer) < 1 else f"{buffer:.2f}%",
            delta="Above minimum" if buffer > 0 else "Below minimum",
            delta_color="normal" if buffer > 0 else "inverse"
        )

    with st.expander("📋 Capital Data Table"):
        st.dataframe(cap_df, use_container_width=True)

st.markdown("---")
st.caption(f"Confidential MIS Report | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
