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

# Display available sheets for debugging
st.write("Available sheets:", xls.sheet_names)

# Parse "Data", "Sheet1" (NPA Data), and "capital" for Capital Adequacy
try:
    sheet_name_data = "Data" if "Data" in xls.sheet_names else xls.sheet_names[0]
    data = xls.parse(sheet_name_data)
    if data.empty:
        st.error("⚠️ Financial Data sheet is empty! Please check the source file.")
        st.stop()
    st.write("Financial Data Columns:", data.columns.tolist())

    npa_data = xls.parse("Sheet1")
    sheet_name_capital = "capital" if "capital" in xls.sheet_names else xls.sheet_names[-1]
    capital_data = xls.parse(sheet_name_capital)
    st.write("Capital Adequacy Columns:", capital_data.columns.tolist())
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

# Function to format data labels
def apply_data_labels(fig, column_data):
    if column_data.notnull().all():
        formatted_labels = [f"{v:.2%}" if isinstance(v, (int, float)) else v for v in column_data]
        fig.update_traces(text=formatted_labels, textposition="top center", mode="lines+text")

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
            apply_data_labels(fig3, npa_data["Gross Npa To Gross Advances"])
            apply_data_labels(fig3, npa_data["Net Npa To Net Advances"])
        
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
        show_data_labels_capital = st.checkbox("📊 Show Data Labels", key="show_labels_capital")
        
        fig4 = px.line(capital_data, x="Month", y=capital_data.columns[1:], 
                       title="🏦 Capital Adequacy Trends", template="plotly_white", markers=True)
        
        if show_data_labels_capital:
            for col in capital_data.columns[1:]:
                apply_data_labels(fig4, capital_data[col])
        
        fig4.update_yaxes(tickformat=".2%")
        fig4 = style_chart(fig4)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.error("⚠️ Capital adequacy data is missing or incorrectly formatted!")
