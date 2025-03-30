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

# Parse "Data", "Sheet1" (NPA Data), and dynamically find "Sheet3"
try:
    data = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
    npa_data = xls.parse("Sheet1")
    
    # Find the correct sheet name for capital adequacy
    sheet_names = xls.sheet_names
    capital_sheet_name = next((s for s in sheet_names if "Sheet3" in s), None)
    
    if capital_sheet_name:
        capital_data = xls.parse(capital_sheet_name)
    else:
        st.error("⚠️ Capital adequacy sheet not found in the file!")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# Function to style charts
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(240, 248, 255, 0.85)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_font=dict(size=18, color="rgb(32, 64, 128)"),
        title_x=0.5,
    )
    return fig

# Dashboard Title
st.title("📊 Financial Dashboard")

# Tabs
tab1, tab2, tab3 = st.tabs(["📜 Financial Data", "📉 NPA Trends", "🏦 Capital Adequacy"])

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
    if required_npa_columns.issubset(npa_data.columns):
        show_data_labels_line = st.checkbox("📊 Show Data Labels", key="show_labels_npa_line")
        
        # Line Chart for Gross vs. Net NPA
        fig3 = px.line(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                       title="📊 Gross vs. Net NPA", template="plotly_white", markers=True)
        
        if show_data_labels_line:
            fig3.update_traces(texttemplate="%{y:.2%}", textposition="top center")
        
        fig3.update_yaxes(tickformat=".2%")
        fig3.update_layout(width=1200, height=600)
        fig3 = style_chart(fig3)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error("⚠️ NPA data is missing required columns!")

### --- Capital Adequacy Tab ---
with tab3:
    st.header("🏦 Capital Adequacy")
    if "Month" in capital_data.columns and len(capital_data.columns) > 1:
        fig4 = px.line(capital_data, x="Month", y=capital_data.columns[1:], 
                       title="🏦 Capital Adequacy Trends", template="plotly_white", markers=True)
        fig4.update_yaxes(tickformat=".2%")
        fig4 = style_chart(fig4)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.error("⚠️ Capital adequacy data is missing or incorrectly formatted!")
