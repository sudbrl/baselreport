import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# GitHub RAW file URL (Make sure it's correct)
GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsm"

# Function to fetch Excel file from GitHub with better error handling
@st.cache_data
def fetch_excel_from_github(url):
    try:
        st.write(f"📡 Fetching data from: {url}")  # Debugging output
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            st.error(f"⚠️ Failed to fetch file! HTTP Status: {response.status_code}")
            st.stop()
        st.write("✅ File fetched successfully!")
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Network error: {e}")
        st.stop()

# Load Excel file from GitHub
try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes))
    st.success("✅ Excel file loaded successfully!")
    st.write(f"📄 Sheets Available: {xls.sheet_names}")  # Debugging output
except Exception as e:
    st.error(f"⚠️ Error loading Excel file: {e}")
    st.stop()

# Parse "Data" sheet
try:
    raw_data = xls.parse("Data")
    columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
    data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])
    st.write("✅ 'Data' sheet loaded successfully!")  # Debugging output
except Exception as e:
    st.error(f"⚠️ Error parsing 'Data' sheet: {e}")
    st.stop()

# Extract NPA-related data from "Data" sheet
try:
    # Debug: Show available column names
    st.write("📄 Available Columns in 'Data' Sheet:", data.columns.tolist())

    # Ensure required columns exist
    if "Particulars" not in data.columns or "Month" not in data.columns or "Rs" not in data.columns:
        st.error("⚠️ Required columns ('Particulars', 'Month', 'Rs') not found in 'Data' sheet!")
        st.stop()

    # Filter NPA-related data
    npa_filtered = data[data["Particulars"].isin(["Gross NPA To Gross Advances", "Net NPA To Net Advances"])]

    # Pivot data to get 'Gross NPA' & 'Net NPA' as separate columns
    npa_data = npa_filtered.pivot(index="Month", columns="Particulars", values="Rs").reset_index()

    # Rename columns for better readability
    npa_data = npa_data.rename(columns={"Gross NPA To Gross Advances": "Gross NPA", "Net NPA To Net Advances": "Net NPA"})

    st.write("✅ NPA Data Extracted Successfully!", npa_data.head())  # Debugging output

except Exception as e:
    st.error(f"⚠️ Error extracting NPA data from 'Data' sheet: {e}")
    st.stop()

# Initialize session state variables if not already set
if "particulars_selected" not in st.session_state:
    st.session_state["particulars_selected"] = ["All"]
if "month_selected" not in st.session_state:
    st.session_state["month_selected"] = ["All"]

# Function to reset filters
def reset_filters():
    st.session_state["particulars_selected"] = ["All"]
    st.session_state["month_selected"] = ["All"]

# Dashboard Title
st.title("📊 Financial Dashboard")

# Tabs for different datasets
tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("📜 Financial Data Overview")

    # Create a 2-column layout (Filters on left, Data/Charts on right)
    col_filters, col_content = st.columns([1, 3])

    with col_filters:
        st.subheader("🔍 Filters")

        # Multi-select filter for "Particulars"
        particulars_options = list(data["Particulars"].dropna().unique())
        particulars_selected = st.multiselect(
            "Select Particulars:", ["All"] + particulars_options, 
            default=st.session_state["particulars_selected"], 
            key="particulars_selected"
        )

        # Multi-select filter for "Month"
        month_options = list(data["Month"].dropna().unique())
        month_selected = st.multiselect(
            "Select Month:", ["All"] + month_options, 
            default=st.session_state["month_selected"], 
            key="month_selected"
        )

        # Reset Button
        st.button("🔄 Reset Filters", on_click=reset_filters)

        # Remove "All" if other options are selected
        if "All" in particulars_selected and len(particulars_selected) > 1:
            st.session_state["particulars_selected"] = [opt for opt in particulars_selected if opt != "All"]
        if "All" in month_selected and len(month_selected) > 1:
            st.session_state["month_selected"] = [opt for opt in month_selected if opt != "All"]

        # Apply filters
        filtered_data = data.copy()
        if "All" not in st.session_state["particulars_selected"]:
            filtered_data = filtered_data[filtered_data["Particulars"].isin(st.session_state["particulars_selected"])]
        if "All" not in st.session_state["month_selected"]:
            filtered_data = filtered_data[filtered_data["Month"].isin(st.session_state["month_selected"])]

        # Convert **filtered** data to CSV for download
        csv_data = filtered_data.to_csv(index=False).encode("utf-8")

        # Download Button for Filtered Data
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv_data,
            file_name="filtered_financial_data.csv",
            mime="text/csv",
        )

    with col_content:
        st.subheader("📊 Data Table & Trends")

        # Display error message if no matching data
        if filtered_data.empty:
            st.error("⚠️ No data available for the selected filters! Try adjusting your choices.")
        else:
            # Display formatted table
            st.dataframe(filtered_data)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends (From 'Data' Sheet)")

    if not npa_data.empty:
        # Create trend charts for Gross & Net NPA
        fig1 = px.line(npa_data, x="Month", y="Gross NPA", title="📊 Gross NPA To Gross Advances Trend", markers=True)
        fig2 = px.line(npa_data, x="Month", y="Net NPA", title="📊 Net NPA To Net Advances Trend", markers=True)

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Bar Chart Comparing Gross & Net NPA
        fig3 = px.bar(npa_data, x="Month", y=["Gross NPA", "Net NPA"], 
                      barmode='group', title="📊 Comparison of Gross & Net NPA")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error("⚠️ NPA data is missing required columns in the 'Data' sheet!")
