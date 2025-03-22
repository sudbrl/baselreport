import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

st.set_page_config(layout="wide", page_title="Financial Dashboard")

GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsm"

@st.cache_data
def fetch_excel_from_github(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content  

try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes))  
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

raw_data = xls.parse("Data")
columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])

if "particulars_selected" not in st.session_state:
    st.session_state["particulars_selected"] = ["All"]
if "month_selected" not in st.session_state:
    st.session_state["month_selected"] = ["All"]

def reset_filters():
    st.session_state["particulars_selected"] = ["All"]
    st.session_state["month_selected"] = ["All"]

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:  # ✅ FIX: Use "openpyxl"
        df.to_excel(writer, index=False, sheet_name="Filtered Data")
    return output.getvalue()

st.title("📊 Financial Dashboard")

tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

with tab1:
    st.header("📜 Financial Data Overview")

    col_filters, col_content = st.columns([1, 3])

    with col_filters:
        st.subheader("🔍 Filters")

        particulars_options = list(data["Particulars"].dropna().unique())
        particulars_selected = st.multiselect(
            "Select Particulars:", ["All"] + particulars_options, 
            default=st.session_state["particulars_selected"], 
            key="particulars_selected"
        )

        month_options = list(data["Month"].dropna().unique())
        month_selected = st.multiselect(
            "Select Month:", ["All"] + month_options, 
            default=st.session_state["month_selected"], 
            key="month_selected"
        )

        st.button("🔄 Reset Filters", on_click=reset_filters)

        if not data.empty:
            excel_data = convert_df_to_excel(data)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_filtered_data",
                use_container_width=True,
            )

        if "All" in particulars_selected and len(particulars_selected) > 1:
            st.session_state["particulars_selected"] = [opt for opt in particulars_selected if opt != "All"]
        if "All" in month_selected and len(month_selected) > 1:
            st.session_state["month_selected"] = [opt for opt in month_selected if opt != "All"]

    filtered_data = data.copy()
    if "All" not in st.session_state["particulars_selected"]:
        filtered_data = filtered_data[filtered_data["Particulars"].isin(st.session_state["particulars_selected"])]
    if "All" not in st.session_state["month_selected"]:
        filtered_data = filtered_data[filtered_data["Month"].isin(st.session_state["month_selected"])]

    if filtered_data.empty:
        st.error("⚠️ No data available for the selected filters! Try adjusting your choices.")
    else:
        with col_content:
            st.subheader("📊 Data Table & Trends")
            st.dataframe(filtered_data, height=400)

            if "All" not in st.session_state["particulars_selected"]:
                fig = px.line(filtered_data, x="Month", y="Rs", 
                              title=f"📈 Trend for {', '.join(st.session_state['particulars_selected'])}", 
                              template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("📉 NPA Trends")

    try:
        npa_data = xls.parse("Sheet1")
        required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
        if required_npa_columns.issubset(npa_data.columns):
            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", 
                               title="📊 Gross NPA To Gross Advances Trend", template="plotly_white")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", 
                               title="📊 Net NPA To Net Advances Trend", template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)

            fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                          barmode='group', title="📊 Comparison of Gross & Net NPA", template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.error("⚠️ NPA data is missing required columns!")
    except Exception as e:
        st.error(f"⚠️ Error parsing 'NPA Data' sheet: {e}")
