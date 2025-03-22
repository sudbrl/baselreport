import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# Set page configuration
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# GitHub file URL (RAW version)
GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsm"

# Function to fetch Excel file from GitHub
@st.cache_data
def fetch_excel_from_github(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content  # Cache only raw file content (bytes)

# Load Excel file from GitHub
try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes))  # Process the Excel file dynamically
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()  # Stop execution if data cannot be fetched

# Parse "Data" sheet
try:
    raw_data = xls.parse("Data")
    columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
    data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])
except Exception as e:
    st.error(f"⚠️ Error parsing 'Data' sheet: {e}")
    st.stop()

# Function to format numerical values
def format_data(df):
    df = df.copy()  # Avoid modifying the original dataframe
    
    # Format currency columns (assuming 'Rs' stores financial values)
    if "Rs" in df.columns:
        df["Rs"] = df["Rs"].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "N/A")  # ₹ currency, comma separator, 2 decimals
    
    # Format percentage columns (assuming 'Movements(%)' is a percentage)
    if "Movements(%)" in df.columns:
        df["Movements(%)"] = df["Movements(%)"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")  # Retain 2 decimal places with %

    # Format other numerical columns (e.g., large numbers in '000' format)
    for col in df.select_dtypes(include=['number']).columns:
        if col not in ["Rs", "Movements(%)"]:  # Exclude already formatted columns
            df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")  # Add thousands separator, no decimals
    
    return df

# Apply formatting to data
formatted_data = format_data(data)

# Display formatted data in a nice table using Pandas Styler
st.subheader("📊 Formatted Financial Data Table")
st.dataframe(
    formatted_data.style.format(  # Apply styling
        {
            "Rs": "{:,.2f}",  # Two decimal places with comma separator
            "Movements(%)": "{:.2f}%",  # Retain two decimals
        }
    ).set_table_styles(
        [
            {"selector": "thead th", "props": [("font-size", "14px"), ("background-color", "#3498db"), ("color", "white")]},
            {"selector": "tbody td", "props": [("text-align", "right")]}
        ]
    ),
    height=400
)

# Convert formatted data to CSV for download
csv_data = formatted_data.to_csv(index=False).encode("utf-8")

# Add a download button below the filters
st.download_button(
    label="📥 Download Filtered Data",
    data=csv_data,
    file_name="filtered_financial_data.csv",
    mime="text/csv",
)
