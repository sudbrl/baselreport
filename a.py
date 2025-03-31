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

# Parse "Data" and "Sheet1" (NPA Data)
try:
    data = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
    npa_data = xls.parse("Sheet1")
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# Function to format values for display
def format_label(value, is_percentage=False):
    if isinstance(value, (int, float)):
        if is_percentage:
            return f"{value * 100:.2f}%"  # Format as percentage
        elif abs(value) < 1 and value != 0:
            return f"{value * 100:.2f}%"  # Format as percentage
        return f"{value:,.0f}"  # Format large numbers with commas
    return value  

# Function to apply formatting to dataframe
def format_dataframe(df):
    df_copy = df.copy()
    
    # Identify which columns are percentages (e.g., columns containing the word 'Npa' or 'Rs')
    for col in df_copy.select_dtypes(include=['float', 'int']):
        is_percentage = any(substring in col.lower() for substring in ["npa", "to", "advance", "rs"])
        df_copy[col] = df_copy[col].apply(lambda x: format_label(x, is_percentage))
    return df_copy

# Function to apply formatted data labels to charts
def apply_data_labels(fig, column_data, is_percentage=False):
    formatted_labels = [format_label(v, is_percentage) for v in column_data]
    fig.update_traces(text=formatted_labels, textposition="top center", mode="lines+text")

# Function to apply fancy styling to the charts
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
tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

with tab2:
    st.header("📉 NPA Trends")

    required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
    if required_npa_columns.issubset(npa_data.columns):

        col1, col2 = st.columns(2)

        with col1:
            show_data_labels_gross = st.checkbox("📊 Show Data Labels", key="show_labels_gross_npa")
            fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", title="📊 Gross NPA Trend", 
                           template="plotly_white", markers=True)
            if show_data_labels_gross:
                apply_data_labels(fig1, npa_data["Gross Npa To Gross Advances"], is_percentage=True)
            fig1.update_yaxes(tickformat=".2%")
            fig1.update_layout(width=1200, height=600)
            fig1 = style_chart(fig1)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            show_data_labels_net = st.checkbox("📊 Show Data Labels", key="show_labels_net_npa")
            fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", title="📊 Net NPA Trend", 
                           template="plotly_white", markers=True)
            if show_data_labels_net:
                apply_data_labels(fig2, npa_data["Net Npa To Net Advances"], is_percentage=True)
            fig2.update_yaxes(tickformat=".2%")
            fig2.update_layout(width=1200, height=600)
            fig2 = style_chart(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        show_data_labels_bar = st.checkbox("📊 Show Data Labels", key="show_labels_bar_npa")
        fig3 = px.line(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                      title="📊 Gross vs. Net NPA", template="plotly_white", markers=True)
        
        if show_data_labels_bar:
            for trace in fig3.data:
                trace.text = [f"{y:.2%}" for y in trace.y]
                trace.textposition = "top center"
        
        fig3.update_yaxes(tickformat=".2%")
        fig3.update_layout(width=1200, height=600)
        fig3 = style_chart(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.error("⚠️ NPA data is missing required columns!")
