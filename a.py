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

# Parse "Sheet1" (NPA Data)
try:
    npa_data = xls.parse("Sheet1")
except Exception as e:
    st.error(f"⚠️ Error parsing 'Sheet1' (NPA Data): {e}")
    st.stop()

# Initialize session state variables
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

        # Convert "Rs" column to numeric safely
        filtered_data["Rs"] = pd.to_numeric(filtered_data["Rs"], errors="coerce").fillna(0)

        # Convert large numbers to Crores
        filtered_data["Rs"] = filtered_data["Rs"].apply(lambda x: round(x / 1_00_00_000, 2) if x >= 1_00_00_000 else x)

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
            # Show "Amount in Cr" only if numbers are in Crores
            if filtered_data["Rs"].max() >= 1:
                st.caption("💰 Amount in Cr")

            # Display formatted table
            st.dataframe(filtered_data, height=400)

            # Toggle for Data Labels
            show_labels = st.checkbox("📝 Show Data Labels", value=True)

            # Trend Chart for Selected Particulars
            if "All" not in st.session_state["particulars_selected"]:
                fig = px.line(filtered_data, x="Month", y="Rs", 
                              title="📈 Financial Trend", 
                              text="Rs" if show_labels else None, 
                              template="plotly_white")

                fig.update_traces(textposition="top center")

                st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    # Validate NPA Data Columns
    required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
    if required_npa_columns.issubset(npa_data.columns):

        # Data Labels Toggle for NPA Charts
        show_npa_labels = st.checkbox("📝 Show NPA Data Labels", value=True)

        # Create a 2-column layout for charts
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", 
                           title="📊 Gross NPA To Gross Advances Trend", 
                           text="Gross Npa To Gross Advances" if show_npa_labels else None, 
                           template="plotly_white")
            fig1.update_traces(texttemplate="%{text:.1%}", textposition="top center")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", 
                           title="📊 Net NPA To Net Advances Trend", 
                           text="Net Npa To Net Advances" if show_npa_labels else None, 
                           template="plotly_white")
            fig2.update_traces(texttemplate="%{text:.1%}", textposition="top center")
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.error("⚠️ NPA data is missing required columns!")
