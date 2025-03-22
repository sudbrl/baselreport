import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import xlsxwriter

# ✅ Set Streamlit Page Config (MUST be the first command)
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# ✅ GitHub Excel File URL
GITHUB_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsm"

# ✅ Function to Load Data from GitHub
@st.cache_data
def load_data():
    response = requests.get(GITHUB_URL)
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)
        xls = pd.ExcelFile(excel_data)
        
        # ✅ Return dictionary of DataFrames instead of ExcelFile
        return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    else:
        st.error("❌ Failed to load data from GitHub. Please check the file URL.")
        return None

# Load Data
xls_sheets = load_data()
if xls_sheets is not None:
    # ✅ Extract sheets as DataFrames
    data = xls_sheets.get("Data", pd.DataFrame())
    npa_data = xls_sheets.get("Sheet1", pd.DataFrame())

    # ✅ Drop unnecessary columns
    columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
    data = data.drop(columns=[col for col in columns_to_drop if col in data.columns], errors="ignore")

# ✅ Custom Styling
st.markdown(
    """
    <style>
        .main {background-color: #f4f4f9;}
        div.block-container {padding: 20px;}
        .stButton>button {background-color: #007BFF; color: white; font-weight: bold; border-radius: 5px; padding: 6px 10px; font-size: 12px;}
        .stButton>button:hover {background-color: #0056b3;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ Sidebar Filters
st.sidebar.header("🔍 Filters")
particulars_options = ["All"] + list(data["Particulars"].dropna().unique())
date_options = ["All"] + list(data["Month"].dropna().unique())

# Multi-select for Particulars
selected_particulars = st.sidebar.multiselect("Select Particulars:", particulars_options, default=["All"])
selected_months = st.sidebar.multiselect("Select Month:", date_options, default=["All"])

# Remove "All" if user selects other values
if "All" in selected_particulars and len(selected_particulars) > 1:
    selected_particulars.remove("All")
if "All" in selected_months and len(selected_months) > 1:
    selected_months.remove("All")

# ✅ Apply Filters
filtered_data = data.copy()
if "All" not in selected_particulars:
    filtered_data = filtered_data[filtered_data["Particulars"].isin(selected_particulars)]
if "All" not in selected_months:
    filtered_data = filtered_data[filtered_data["Month"].isin(selected_months)]

# ✅ Reset Filters
def reset_filters():
    st.session_state["selected_particulars"] = ["All"]
    st.session_state["selected_months"] = ["All"]
    st.rerun()

col_reset, col_download = st.sidebar.columns([1, 1])

with col_reset:
    st.button("🔄 Reset", on_click=reset_filters)

# ✅ Download Filtered Data
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered Data")
    return output.getvalue()

with col_download:
    st.download_button(
        label="⬇ Excel",
        data=convert_df_to_excel(filtered_data),
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ✅ Dashboard Layout (2-Column Design)
col1, col2 = st.columns([1, 2])

# ✅ Data Table on Right
with col2:
    st.subheader("📊 Filtered Financial Data")
    st.dataframe(filtered_data, height=400)

    # ✅ Line Chart if a particular is selected
    if len(selected_particulars) == 1 and "All" not in selected_particulars:
        fig = px.line(filtered_data, x="Month", y="Rs", 
                      title=f"📈 Trend for {selected_particulars[0]}", 
                      template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ✅ NPA Trends Section
st.subheader("📉 NPA Trends")
if {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}.issubset(npa_data.columns):
    col3, col4 = st.columns(2)

    with col3:
        fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", 
                       title="📊 Gross NPA To Gross Advances Trend", template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

    with col4:
        fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", 
                       title="📊 Net NPA To Net Advances Trend", template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    # ✅ Bar Chart Comparison
    fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                  barmode='group', title="📊 Comparison of Gross & Net NPA", template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.error("⚠️ NPA data is missing required columns!")
