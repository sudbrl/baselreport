import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import BytesIO
from datetime import datetime
import numpy as np

# ---------------------- Page Configuration ----------------------

st.set_page_config(
    page_title="Financial Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- Custom CSS Styling ----------------------

st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* KPI Card Styling */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px 0 rgba(31, 38, 135, 0.5);
    }
    
    .kpi-title {
        color: #667eea;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        color: #2d3748;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .kpi-change {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .kpi-change.positive {
        color: #48bb78;
    }
    
    .kpi-change.negative {
        color: #f56565;
    }
    
    /* Filter Section */
    .filter-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 1rem;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Download button styling */
    .stDownloadButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 16px 0 rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px 0 rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- Data Loading ----------------------

@st.cache_data
def fetch_excel_from_github(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"

try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes))
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

# ---------------------- Data Parsing ----------------------

try:
    data = xls.parse("Data").drop(
        columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"],
        errors="ignore"
    )
    npa_data = xls.parse("Sheet1")
    capital_data = xls.parse("capital")
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# ---------------------- Formatting Helpers ----------------------

def format_label(value, is_percentage=False):
    if isinstance(value, (int, float)):
        if is_percentage or (abs(value) < 1 and value != 0):
            return f"{value * 100:.2f}%"
        return f"{value:,.0f}"
    return value

def format_dataframe(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['float', 'int']):
        is_percentage = any(s in col.lower() for s in ["npa", "to", "advance", "rs", "capital"])
        df_copy[col] = df_copy[col].apply(lambda x: format_label(x, is_percentage))
    return df_copy

def create_modern_chart(df, x, y, title, chart_type="line", color=None):
    """Create a modern styled chart with gradient colors"""
    
    if chart_type == "line":
        fig = go.Figure()
        
        if isinstance(y, list):
            colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
            for i, col in enumerate(y):
                fig.add_trace(go.Scatter(
                    x=df[x],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8, line=dict(width=2, color='white')),
                    hovertemplate='<b>%{y:.2%}</b><extra></extra>' if 'npa' in col.lower() or 'capital' in col.lower() else '<b>%{y:,.0f}</b><extra></extra>'
                ))
        else:
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[y],
                mode='lines+markers',
                name=y,
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, line=dict(width=2, color='white')),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))
    
    elif chart_type == "bar":
        if isinstance(y, list):
            fig = go.Figure()
            colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
            for i, col in enumerate(y):
                fig.add_trace(go.Bar(
                    x=df[x],
                    y=df[col],
                    name=col,
                    marker_color=colors[i % len(colors)],
                    text=df[col].apply(lambda v: f"{v:.2%}" if v < 1 else f"{v:,.0f}"),
                    textposition='outside'
                ))
        else:
            fig = go.Figure(go.Bar(
                x=df[x],
                y=df[y],
                marker_color='#667eea',
                text=df[y].apply(lambda v: f"{v:.2%}" if v < 1 else f"{v:,.0f}"),
                textposition='outside'
            ))
    
    elif chart_type == "area":
        fig = go.Figure()
        colors = ['rgba(102, 126, 234, 0.6)', 'rgba(118, 75, 162, 0.6)']
        for i, col in enumerate(y):
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[col],
                mode='lines',
                name=col,
                fill='tonexty' if i > 0 else 'tozeroy',
                line=dict(width=2),
                fillcolor=colors[i % len(colors)]
            ))
    
    # Styling
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2d3748', 'family': 'Arial, sans-serif', 'weight': 'bold'}
        },
        plot_bgcolor='rgba(255, 255, 255, 0.9)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            tickfont=dict(size=12, color='#4a5568')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            tickfont=dict(size=12, color='#4a5568')
        ),
        hovermode='x unified',
        margin=dict(l=60, r=60, t=80, b=60),
        font=dict(family="Arial, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(200, 200, 200, 0.5)',
            borderwidth=1
        )
    )
    
    return fig

# ---------------------- Header ----------------------

st.markdown("""
<div class="main-header">
    <h1>📊 Financial Analytics Dashboard</h1>
    <p>Real-time insights and comprehensive financial analysis</p>
</div>
""", unsafe_allow_html=True)

# ---------------------- Key Metrics Summary ----------------------

st.markdown("### 📈 Key Performance Indicators")

# Calculate key metrics
latest_npa = npa_data.iloc[-1]
prev_npa = npa_data.iloc[-2] if len(npa_data) > 1 else npa_data.iloc[-1]

latest_capital = capital_data.iloc[-1]
prev_capital = capital_data.iloc[-2] if len(capital_data) > 1 else capital_data.iloc[-1]

gross_npa_change = ((latest_npa["Gross Npa To Gross Advances"] - prev_npa["Gross Npa To Gross Advances"]) / prev_npa["Gross Npa To Gross Advances"]) * 100
net_npa_change = ((latest_npa["Net Npa To Net Advances"] - prev_npa["Net Npa To Net Advances"]) / prev_npa["Net Npa To Net Advances"]) * 100
core_capital_change = ((latest_capital["Core Capital%"] - prev_capital["Core Capital%"]) / prev_capital["Core Capital%"]) * 100
total_capital_change = ((latest_capital["Total Capital%"] - prev_capital["Total Capital%"]) / prev_capital["Total Capital%"]) * 100

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Gross NPA Ratio</div>
        <div class="kpi-value">{latest_npa["Gross Npa To Gross Advances"]:.2%}</div>
        <div class="kpi-change {'positive' if gross_npa_change < 0 else 'negative'}">
            {'▼' if gross_npa_change < 0 else '▲'} {abs(gross_npa_change):.2f}% vs previous
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Net NPA Ratio</div>
        <div class="kpi-value">{latest_npa["Net Npa To Net Advances"]:.2%}</div>
        <div class="kpi-change {'positive' if net_npa_change < 0 else 'negative'}">
            {'▼' if net_npa_change < 0 else '▲'} {abs(net_npa_change):.2f}% vs previous
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Core Capital</div>
        <div class="kpi-value">{latest_capital["Core Capital%"]:.2%}</div>
        <div class="kpi-change {'positive' if core_capital_change > 0 else 'negative'}">
            {'▲' if core_capital_change > 0 else '▼'} {abs(core_capital_change):.2f}% vs previous
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Capital</div>
        <div class="kpi-value">{latest_capital["Total Capital%"]:.2%}</div>
        <div class="kpi-change {'positive' if total_capital_change > 0 else 'negative'}">
            {'▲' if total_capital_change > 0 else '▼'} {abs(total_capital_change):.2f}% vs previous
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------- Tabs ----------------------

tab1, tab2, tab3, tab4 = st.tabs(["📜 Financial Data", "📉 NPA Analysis", "💼 Capital Adequacy", "📊 Comprehensive View"])

# ---------------------- Tab 1: Financial Data ----------------------

with tab1:
    st.markdown("### 📜 Financial Data Overview")
    
    col_filters, col_content = st.columns([1, 3])
    
    with col_filters:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Filters")
        
        if "particulars_selected" not in st.session_state:
            st.session_state["particulars_selected"] = ["All"]
        if "month_selected" not in st.session_state:
            st.session_state["month_selected"] = ["All"]
        
        particulars_selected = st.multiselect(
            "Select Particulars:",
            ["All"] + list(data["Particulars"].dropna().unique()),
            default=st.session_state["particulars_selected"],
            key="particulars_filter"
        )
        
        month_selected = st.multiselect(
            "Select Month:",
            ["All"] + list(data["Month"].dropna().unique()),
            default=st.session_state["month_selected"],
            key="month_filter"
        )
        
        if st.button("🔄 Reset Filters", key="reset_filters"):
            st.session_state["particulars_selected"] = ["All"]
            st.session_state["month_selected"] = ["All"]
            st.rerun()
        
        # Apply filters
        filtered_data = data.copy()
        if "All" not in particulars_selected:
            filtered_data = filtered_data[filtered_data["Particulars"].isin(particulars_selected)]
        if "All" not in month_selected:
            filtered_data = filtered_data[filtered_data["Month"].isin(month_selected)]
        
        csv_data = filtered_data.to_csv(index=False).encode("utf-8")
        file_name = f"filtered_financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        st.download_button(
            "📥 Download Data",
            data=csv_data,
            file_name=file_name,
            mime="text/csv",
            key="download_financial"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_content:
        if filtered_data.empty:
            st.warning("⚠️ No data available for the selected filters!")
        else:
            # Data table
            st.markdown("#### 📊 Data Table")
            styled_data = format_dataframe(filtered_data)
            st.dataframe(styled_data, height=400, use_container_width=True)
            
            # Chart
            if "All" not in particulars_selected and len(particulars_selected) > 0:
                st.markdown("#### 📈 Trend Analysis")
                
                show_data_labels = st.checkbox("Show Data Labels", key="show_labels_financial")
                
                fig = create_modern_chart(
                    filtered_data,
                    x="Month",
                    y="Rs",
                    title=f"Trend: {', '.join(particulars_selected[:3])}{'...' if len(particulars_selected) > 3 else ''}",
                    chart_type="line"
                )
                
                if show_data_labels:
                    fig.update_traces(
                        text=[f"{v:,.0f}" for v in filtered_data["Rs"]],
                        textposition="top center",
                        mode="lines+markers+text"
                    )
                
                st.plotly_chart(fig, use_container_width=True)

# ---------------------- Tab 2: NPA Analysis ----------------------

with tab2:
    st.markdown("### 📉 Non-Performing Assets Analysis")
    
    # NPA Trend Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_gross = create_modern_chart(
            npa_data,
            x="Month",
            y="Gross Npa To Gross Advances",
            title="Gross NPA Trend",
            chart_type="line"
        )
        fig_gross.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig_gross, use_container_width=True)
    
    with col2:
        fig_net = create_modern_chart(
            npa_data,
            x="Month",
            y="Net Npa To Net Advances",
            title="Net NPA Trend",
            chart_type="line"
        )
        fig_net.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig_net, use_container_width=True)
    
    # Comparative Bar Chart
    st.markdown("#### 📊 Comparative Analysis")
    fig_compare = create_modern_chart(
        npa_data,
        x="Month",
        y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"],
        title="Gross vs Net NPA Comparison",
        chart_type="bar"
    )
    fig_compare.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # NPA Statistics
    st.markdown("#### 📈 NPA Statistics")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric(
            "Average Gross NPA",
            f"{npa_data['Gross Npa To Gross Advances'].mean():.2%}",
            f"{npa_data['Gross Npa To Gross Advances'].std():.2%} std"
        )
    
    with stat_col2:
        st.metric(
            "Average Net NPA",
            f"{npa_data['Net Npa To Net Advances'].mean():.2%}",
            f"{npa_data['Net Npa To Net Advances'].std():.2%} std"
        )
    
    with stat_col3:
        st.metric(
            "Lowest Gross NPA",
            f"{npa_data['Gross Npa To Gross Advances'].min():.2%}",
            f"{npa_data[npa_data['Gross Npa To Gross Advances'] == npa_data['Gross Npa To Gross Advances'].min()]['Month'].values[0]}"
        )
    
    with stat_col4:
        st.metric(
            "Lowest Net NPA",
            f"{npa_data['Net Npa To Net Advances'].min():.2%}",
            f"{npa_data[npa_data['Net Npa To Net Advances'] == npa_data['Net Npa To Net Advances'].min()]['Month'].values[0]}"
        )

# ---------------------- Tab 3: Capital Adequacy ----------------------

with tab3:
    st.markdown("### 💼 Capital Adequacy Ratios")
    
    # Capital Trend Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_core = create_modern_chart(
            capital_data,
            x="Month",
            y="Core Capital%",
            title="Core Capital Ratio",
            chart_type="line"
        )
        fig_core.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig_core, use_container_width=True)
    
    with col2:
        fig_total = create_modern_chart(
            capital_data,
            x="Month",
            y="Total Capital%",
            title="Total Capital Ratio",
            chart_type="line"
        )
        fig_total.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig_total, use_container_width=True)
    
    # Combined Capital Chart
    st.markdown("#### 📊 Capital Comparison")
    fig_capital = create_modern_chart(
        capital_data,
        x="Month",
        y=["Core Capital%", "Total Capital%"],
        title="Core vs Total Capital",
        chart_type="area"
    )
    fig_capital.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig_capital, use_container_width=True)
    
    # Capital Statistics
    st.markdown("#### 📈 Capital Statistics")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric(
            "Average Core Capital",
            f"{capital_data['Core Capital%'].mean():.2%}",
            f"{capital_data['Core Capital%'].std():.2%} std"
        )
    
    with stat_col2:
        st.metric(
            "Average Total Capital",
            f"{capital_data['Total Capital%'].mean():.2%}",
            f"{capital_data['Total Capital%'].std():.2%} std"
        )
    
    with stat_col3:
        st.metric(
            "Max Core Capital",
            f"{capital_data['Core Capital%'].max():.2%}",
            f"{capital_data[capital_data['Core Capital%'] == capital_data['Core Capital%'].max()]['Month'].values[0]}"
        )
    
    with stat_col4:
        st.metric(
            "Max Total Capital",
            f"{capital_data['Total Capital%'].max():.2%}",
            f"{capital_data[capital_data['Total Capital%'] == capital_data['Total Capital%'].max()]['Month'].values[0]}"
        )

# ---------------------- Tab 4: Comprehensive View ----------------------

with tab4:
    st.markdown("### 📊 Comprehensive Financial Overview")
    
    # Create a comprehensive dashboard with multiple charts
    
    # Row 1: NPA and Capital Side by Side
    st.markdown("#### Risk & Capital Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        # NPA Combined Chart
        fig_npa_combined = go.Figure()
        fig_npa_combined.add_trace(go.Scatter(
            x=npa_data["Month"],
            y=npa_data["Gross Npa To Gross Advances"],
            mode='lines+markers',
            name='Gross NPA',
            line=dict(color='#f56565', width=3),
            marker=dict(size=8)
        ))
        fig_npa_combined.add_trace(go.Scatter(
            x=npa_data["Month"],
            y=npa_data["Net Npa To Net Advances"],
            mode='lines+markers',
            name='Net NPA',
            line=dict(color='#48bb78', width=3),
            marker=dict(size=8)
        ))
        fig_npa_combined.update_layout(
            title="NPA Ratios Over Time",
            plot_bgcolor='rgba(255, 255, 255, 0.9)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            yaxis_tickformat=".2%",
            hovermode='x unified'
        )
        st.plotly_chart(fig_npa_combined, use_container_width=True)
    
    with col2:
        # Capital Combined Chart
        fig_capital_combined = go.Figure()
        fig_capital_combined.add_trace(go.Scatter(
            x=capital_data["Month"],
            y=capital_data["Core Capital%"],
            mode='lines+markers',
            name='Core Capital',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        fig_capital_combined.add_trace(go.Scatter(
            x=capital_data["Month"],
            y=capital_data["Total Capital%"],
            mode='lines+markers',
            name='Total Capital',
            line=dict(color='#764ba2', width=3),
            marker=dict(size=8)
        ))
        fig_capital_combined.update_layout(
            title="Capital Ratios Over Time",
            plot_bgcolor='rgba(255, 255, 255, 0.9)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            yaxis_tickformat=".2%",
            hovermode='x unified'
        )
        st.plotly_chart(fig_capital_combined, use_container_width=True)
    
    # Row 2: Summary Statistics
    st.markdown("#### 📊 Summary Statistics")
    
    # Create summary dataframe
    summary_data = pd.DataFrame({
        'Metric': ['Gross NPA', 'Net NPA', 'Core Capital', 'Total Capital'],
        'Current': [
            f"{latest_npa['Gross Npa To Gross Advances']:.2%}",
            f"{latest_npa['Net Npa To Net Advances']:.2%}",
            f"{latest_capital['Core Capital%']:.2%}",
            f"{latest_capital['Total Capital%']:.2%}"
        ],
        'Average': [
            f"{npa_data['Gross Npa To Gross Advances'].mean():.2%}",
            f"{npa_data['Net Npa To Net Advances'].mean():.2%}",
            f"{capital_data['Core Capital%'].mean():.2%}",
            f"{capital_data['Total Capital%'].mean():.2%}"
        ],
        'Min': [
            f"{npa_data['Gross Npa To Gross Advances'].min():.2%}",
            f"{npa_data['Net Npa To Net Advances'].min():.2%}",
            f"{capital_data['Core Capital%'].min():.2%}",
            f"{capital_data['Total Capital%'].min():.2%}"
        ],
        'Max': [
            f"{npa_data['Gross Npa To Gross Advances'].max():.2%}",
            f"{npa_data['Net Npa To Net Advances'].max():.2%}",
            f"{capital_data['Core Capital%'].max():.2%}",
            f"{capital_data['Total Capital%'].max():.2%}"
        ]
    })
    
    st.dataframe(summary_data, use_container_width=True, hide_index=True)
    
    # Download comprehensive report
    st.markdown("#### 📥 Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        npa_csv = npa_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download NPA Data",
            data=npa_csv,
            file_name=f"npa_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        capital_csv = capital_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Capital Data",
            data=capital_csv,
            file_name=f"capital_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col3:
        summary_csv = summary_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Summary",
            data=summary_csv,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ---------------------- Footer ----------------------

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 2rem;'>
    <p style='font-size: 0.9rem;'>📊 Financial Analytics Dashboard | Last updated: {}</p>
    <p style='font-size: 0.8rem; opacity: 0.8;'>Powered by Streamlit & Plotly</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
