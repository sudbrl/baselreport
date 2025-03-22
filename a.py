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
    st.stop()

# Parse "Data" sheet
raw_data = xls.parse("Data")
columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])

# Initialize session state variables
if "particulars_selected" not in st.session_state:
    st.session_state["particulars_selected"] = ["All"]
if "month_selected" not in st.session_state:
    st.session_state["month_selected"] = ["All"]

# Function to reset filters
def reset_filters():
    st.session_state["particulars_selected"] = ["All"]
    st.session_state["month_selected"] = ["All"]

# Function to convert DataFrame to Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered Data")
    processed_data = output.getvalue()
    return processed_data

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

        # 📥 Small Download Button (Below Reset)
        if not data.empty:
            st.markdown(
                "<style>.small-btn {text-align: center; padding: 5px;}</style>",
                unsafe_allow_html=True,
            )
            excel_data = convert_df_to_excel(data)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Click to download the filtered data",
                key="download_filtered_data",
                use_container_width=True,
            )

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

    # Display error message if no matching data
    if filtered_data.empty:
        st.error("⚠️ No data available for the selected filters! Try adjusting your choices.")
    else:
        with col_content:
            st.subheader("📊 Data Table & Trends")

            # Display formatted table
            st.dataframe(filtered_data.style.set_properties(**{'text-align': 'left'}).set_table_styles(
                [{'selector': 'thead th', 'props': [('font-size', '14px'), ('background-color', '#3498db'), ('color', 'white')]}]
            ), height=400)

            # Trend Chart for Selected Particulars
            if "All" not in st.session_state["particulars_selected"]:
                fig = px.line(filtered_data, x="Month", y="Rs", 
                              title=f"📈 Trend for {', '.join(st.session_state['particulars_selected'])}", 
                              template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    # Parse "NPA Data" sheet
    try:
        npa_data = xls.parse("Sheet1")
        required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
        if required_npa_columns.issubset(npa_data.columns):
            # Create a 2-column layout for charts
            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", 
                               title="📊 Gross NPA To Gross Advances Trend", template="plotly_white")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", 
                               title="📊 Net NPA To Net Advances Trend", template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)

            # Bar Chart Comparing Gross & Net NPA
            fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                          barmode='group', title="📊 Comparison of Gross & Net NPA", template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.error("⚠️ NPA data is missing required columns!")
    except Exception as e:
        st.error(f"⚠️ Error parsing 'NPA Data' sheet: {e}")
