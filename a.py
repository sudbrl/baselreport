import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from datetime import datetime

# Function to fetch Excel file from GitHub
@st.cache_data
def fetch_excel_from_github(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

# Load Excel file from GitHub
GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes)) 
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

# Parse "Data", "Sheet1" (NPA Data), and "Capital" sheet
try:
    data = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
    npa_data = xls.parse("Sheet1")
    capital_data = xls.parse("Capital")
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# Function to format values for display
def format_label(value, is_percentage=False):
    if isinstance(value, (int, float)):
        if is_percentage:
            return f"{value * 100:.2f}%"
        elif abs(value) < 1 and value != 0:
            return f"{value * 100:.2f}%"
        return f"{value:,.0f}"
    return value  

# Function to apply formatted data labels to charts
def apply_data_labels(fig, column_data, is_percentage=False):
    formatted_labels = [format_label(v, is_percentage) for v in column_data]
    fig.update_traces(text=formatted_labels, textposition="top center", mode="lines+text")

# Function to apply fancy styling to charts
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(240, 248, 255, 0.85)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_font=dict(size=18, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        xaxis_title_font=dict(size=14, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        yaxis_title_font=dict(size=14, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        title_x=0.5,
        xaxis=dict(tickfont=dict(size=12, color="rgb(32, 64, 128)")),
        yaxis=dict(tickfont=dict(size=12, color="rgb(32, 64, 128)")),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    return fig

# Dashboard Title
st.title("📊 Financial Dashboard")

# Tabs
tab1, tab2, tab3 = st.tabs(["📜 Financial Data", "📉 NPA Trends", "🏦 Capital Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("📜 Financial Data Overview")
    st.dataframe(data)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")
    
    if {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}.issubset(npa_data.columns):
        fig_npa = px.line(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"],
                          title="📈 NPA Trends", template="plotly_white", markers=True)
        fig_npa.update_yaxes(tickformat=".2%")
        fig_npa = style_chart(fig_npa)
        st.plotly_chart(fig_npa, use_container_width=True)
    else:
        st.error("⚠️ NPA data is missing required columns!")

### --- Capital Trends Tab ---
with tab3:
    st.header("🏦 Capital Adequacy Trends")
    
    required_capital_columns = {"Month", "Capital Adequacy Ratio", "Tier 1 Ratio", "Tier 2 Ratio"}
    if required_capital_columns.issubset(capital_data.columns):
        show_data_labels_cap = st.checkbox("📊 Show Data Labels", key="show_labels_capital")
        
        fig_capital = px.line(capital_data, x="Month", y=["Capital Adequacy Ratio", "Tier 1 Ratio", "Tier 2 Ratio"],
                              title="📈 Capital Adequacy Ratios Over Time", template="plotly_white", markers=True)
        
        if show_data_labels_cap:
            for col in ["Capital Adequacy Ratio", "Tier 1 Ratio", "Tier 2 Ratio"]:
                apply_data_labels(fig_capital, capital_data[col], is_percentage=True)
        
        fig_capital.update_yaxes(tickformat=".2%")
        fig_capital = style_chart(fig_capital)
        st.plotly_chart(fig_capital, use_container_width=True)
    else:
        st.error("⚠️ 'Capital' data is missing required columns!")
