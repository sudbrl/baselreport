import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# Load data from GitHub
GITHUB_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsm"

@st.cache_data
def load_data(url):
    response = requests.get(url)
    file_bytes = io.BytesIO(response.content)
    xls = pd.ExcelFile(file_bytes)

    # Load sheets
    data = xls.parse("Data")
    npa_data = xls.parse("Sheet1")

    # Drop unwanted columns safely
    columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
    data = data.drop(columns=[col for col in columns_to_drop if col in data.columns])

    return data, npa_data

data, npa_data = load_data(GITHUB_URL)

# Set Streamlit page config
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# Custom Styling
st.markdown("""
    <style>
        .main {background-color: #f4f4f9;}
        div.stTitle {color: #2c3e50; text-align: center; font-size: 30px; font-weight: bold;}
        div.block-container {padding: 20px;}
        .download-button {margin-top: 10px;}
    </style>
    """, unsafe_allow_html=True)

# **Session State for Filters**
if "particulars_selected" not in st.session_state:
    st.session_state["particulars_selected"] = ["All"]

if "date_selected" not in st.session_state:
    st.session_state["date_selected"] = ["All"]

# **Filter Reset Function**
def reset_filters():
    st.session_state["particulars_selected"] = ["All"]
    st.session_state["date_selected"] = ["All"]
    st.experimental_rerun()

# **Convert DataFrame to Excel**
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered Data")
    processed_data = output.getvalue()
    return processed_data

# **Dashboard Title**
st.title("📊 Financial Dashboard")

# **Layout: Two-Column Design**
col1, col2 = st.columns([1, 3])

# **Filters (Left Column)**
with col1:
    st.subheader("🔍 Filters")

    # Multi-select for Particulars
    particulars_options = ["All"] + list(data["Particulars"].dropna().unique())
    selected_particulars = st.multiselect("Select Particulars:", particulars_options, 
                                          default=st.session_state["particulars_selected"])

    # Ensure "All" logic
    if "All" in selected_particulars and len(selected_particulars) > 1:
        selected_particulars.remove("All")
    elif not selected_particulars:
        selected_particulars = ["All"]

    # Multi-select for Date
    date_options = ["All"] + list(data["Month"].dropna().unique())
    selected_dates = st.multiselect("Select Month:", date_options, 
                                    default=st.session_state["date_selected"])

    # Ensure "All" logic for Dates
    if "All" in selected_dates and len(selected_dates) > 1:
        selected_dates.remove("All")
    elif not selected_dates:
        selected_dates = ["All"]

    # **Reset Button**
    if st.button("🔄 Reset Filters", help="Click to reset filters"):
        reset_filters()

    # **Download Button**
    filtered_excel = convert_df_to_excel(data)
    st.download_button(label="📥 Download Excel", data=filtered_excel, file_name="filtered_data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       help="Download filtered data", key="download_excel", use_container_width=True)

# **Filtered Data & Charts (Right Column)**
with col2:
    st.subheader("📊 Data Table & Trends")

    # Apply Filters
    filtered_data = data.copy()
    if "All" not in selected_particulars:
        filtered_data = filtered_data[filtered_data["Particulars"].isin(selected_particulars)]
    if "All" not in selected_dates:
        filtered_data = filtered_data[filtered_data["Month"].isin(selected_dates)]

    # **Error Message if No Data**
    if filtered_data.empty:
        st.error("⚠️ No data available for the selected filters. Please adjust your selections.")
    else:
        st.dataframe(filtered_data, height=400, use_container_width=True)

        # **Trend Chart**
        if "All" not in selected_particulars:
            fig = px.line(filtered_data, x="Month", y="Rs", title="📈 Trend Analysis", 
                          template="plotly_white", markers=True)
            st.plotly_chart(fig, use_container_width=True)

# **NPA Data as Separate Tab**
st.markdown("---")
st.subheader("📌 NPA Data Trends")

# Ensure NPA data has required columns
required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
if not required_npa_columns.issubset(npa_data.columns):
    st.error("⚠️ NPA data is missing required columns!")
else:
    # **Side-by-Side Charts for NPA Trends**
    col3, col4 = st.columns(2)
    
    with col3:
        fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", 
                       title="📊 Gross NPA To Gross Advances", template="plotly_white", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

    with col4:
        fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", 
                       title="📊 Net NPA To Net Advances", template="plotly_white", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    # **Comparison Bar Chart**
    fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                  barmode='group', title="📊 Comparison: Gross vs Net NPA", template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)
