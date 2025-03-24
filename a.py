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

            # Trend Chart for Selected Particulars (Multiple Trends)
            if "All" not in st.session_state["particulars_selected"]:
                fig = px.line(
                    filtered_data, x="Month", y="Rs", color="Particulars",
                    title="📈 Trends for Selected Particulars", template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    try:
        # Convert 'Particulars' column to lowercase for case-insensitive matching
        data["Particulars"] = data["Particulars"].str.strip().str.lower()

        # Define the correct case-insensitive search terms
        npa_keywords = ["gross npa to gross advances", "net npa to net advances"]

        # Filter data using case-insensitive search
        npa_filtered = data[data["Particulars"].isin(npa_keywords)]

        # Pivot the data
        npa_data = npa_filtered.pivot(index="Month", columns="Particulars", values="Rs").reset_index()

        # Rename columns for better readability
        npa_data = npa_data.rename(columns={
            "gross npa to gross advances": "Gross NPA",
            "net npa to net advances": "Net NPA"
        })

        # Create a 2-column layout for charts
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(npa_data, x="Month", y="Gross NPA",
                           title="📊 Gross NPA To Gross Advances Trend", template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(npa_data, x="Month", y="Net NPA",
                           title="📊 Net NPA To Net Advances Trend", template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

        # Bar Chart Comparing Gross & Net NPA
        fig3 = px.bar(npa_data, x="Month", y=["Gross NPA", "Net NPA"],
                      barmode='group', title="📊 Comparison of Gross & Net NPA", template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error extracting NPA data from 'Data' sheet: {e}")
