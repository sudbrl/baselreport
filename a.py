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
    return response.content

# Load Excel file from GitHub
try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes)) 
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

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

# Function to format numbers and percentages
def format_values(value):
    if isinstance(value, (int, float)):
        if abs(value) < 1 and value != 0:
            return f"{value:.2%}"  
        else:
            return f"{value:,.0f}"  
    return value  

# Dashboard Title
st.title("📊 Financial Dashboard")

# Tabs for different datasets
tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("📜 Financial Data Overview")

    col_filters, col_content = st.columns([1, 3])

    with col_filters:
        st.subheader("🔍 Filters")

        particulars_options = list(data["Particulars"].dropna().unique())
        particulars_selected = st.multiselect(
            "Select Particulars:", ["All"] + particulars_options, default=["All"]
        )

        month_options = list(data["Month"].dropna().unique())
        month_selected = st.multiselect(
            "Select Month:", ["All"] + month_options, default=["All"]
        )

        st.button("🔄 Reset Filters", on_click=lambda: (st.session_state.update({"particulars_selected": ["All"], "month_selected": ["All"]})))

        filtered_data = data.copy()
        if "All" not in particulars_selected:
            filtered_data = filtered_data[filtered_data["Particulars"].isin(particulars_selected)]
        if "All" not in month_selected:
            filtered_data = filtered_data[filtered_data["Month"].isin(month_selected)]

        csv_data = filtered_data.to_csv(index=False).encode("utf-8")

        st.download_button("📥 Download Filtered Data", data=csv_data, file_name="filtered_financial_data.csv", mime="text/csv")

    with col_content:
        st.subheader("📊 Data Table & Trends")

        if filtered_data.empty:
            st.error("⚠️ No data available for the selected filters! Try adjusting your choices.")
        else:
            styled_data = filtered_data.applymap(format_values)
            st.dataframe(styled_data, height=400)

            if "All" not in particulars_selected:
                # Data Labels Toggle Above Chart
                show_data_labels = st.checkbox("📊 Show Data Labels", key="show_labels_financial")

                fig = px.line(filtered_data, x="Month", y="Rs", title="📈 Financial Trend", template="plotly_white")
                if show_data_labels:
                    fig.update_traces(text=filtered_data["Rs"], textposition="top center", mode="lines+text")
                st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
    if required_npa_columns.issubset(npa_data.columns):

        col1, col2 = st.columns(2)

        with col1:
            # Data Labels Toggle Above Chart
            show_data_labels_gross = st.checkbox("📊 Show Data Labels", key="show_labels_gross_npa")

            fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", title="📊 Gross NPA Trend", template="plotly_white")
            if show_data_labels_gross:
                fig1.update_traces(text=npa_data["Gross Npa To Gross Advances"], textposition="top center", mode="lines+text")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Data Labels Toggle Above Chart
            show_data_labels_net = st.checkbox("📊 Show Data Labels", key="show_labels_net_npa")

            fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", title="📊 Net NPA Trend", template="plotly_white")
            if show_data_labels_net:
                fig2.update_traces(text=npa_data["Net Npa To Net Advances"], textposition="top center", mode="lines+text")
            st.plotly_chart(fig2, use_container_width=True)

        # Data Labels Toggle Above Chart
        show_data_labels_bar = st.checkbox("📊 Show Data Labels", key="show_labels_bar_npa")

        fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                      barmode='group', title="📊 Gross vs. Net NPA", template="plotly_white")
        if show_data_labels_bar:
            fig3.update_traces(texttemplate="%{y:.2%}", textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.error("⚠️ NPA data is missing required columns!")
