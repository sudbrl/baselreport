import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# Function to load Excel file
@st.cache_data
def load_data(file):
    return pd.ExcelFile(file)

# Load file from GitHub (default) or allow upload
github_file_url = "https://raw.githubusercontent.com/sudbrl/baselreport/main/baseldata.xlsm"
uploaded_file = st.file_uploader("Upload Basel Data (XLSM)", type=["xlsm"])

xls = load_data(uploaded_file if uploaded_file else github_file_url)

# Parse "Data" sheet
raw_data = xls.parse("Data")

# Clean data by dropping unwanted columns
columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])

# Parse "Sheet1" (NPA Data)
npa_data = xls.parse("Sheet1")

# Custom CSS for UI styling
st.markdown("""
    <style>
        .main {background-color: #f4f4f9;}
        div.stTitle {color: #2c3e50; text-align: center; font-size: 30px; font-weight: bold;}
        div.block-container {padding: 20px;}
        .stDataFrame {border-radius: 10px; overflow: hidden;}
        .stButton > button {background-color: #3498db; color: white; border-radius: 10px; padding: 5px 10px;}
        .stSelectbox > div {border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

# Dashboard Title
st.title("📊 Financial Dashboard")

# Create a 2-column layout (Filters Left, Data/Charts Right)
col_filters, col_content = st.columns([1, 3])

with col_filters:
    st.header("🔍 Filters")

    # Multi-select filter for "Particulars"
    particulars_options = list(data["Particulars"].dropna().unique())
    particulars_selected = st.multiselect("Select Particulars:", ["All"] + particulars_options, default=["All"])

    # Multi-select filter for "Month"
    month_options = list(data["Month"].dropna().unique())
    month_selected = st.multiselect("Select Month:", ["All"] + month_options, default=["All"])

    # Reset button to clear filters
    if st.button("🔄 Reset Filters"):
        particulars_selected, month_selected = ["All"], ["All"]

    # Remove "All" if other options are selected
    if "All" in particulars_selected and len(particulars_selected) > 1:
        particulars_selected.remove("All")
    if "All" in month_selected and len(month_selected) > 1:
        month_selected.remove("All")

# Apply filters
filtered_data = data.copy()
if "All" not in particulars_selected:
    filtered_data = filtered_data[filtered_data["Particulars"].isin(particulars_selected)]
if "All" not in month_selected:
    filtered_data = filtered_data[filtered_data["Month"].isin(month_selected)]

# --- Display Data Table & Trends ---
with col_content:
    st.header("📊 Data Table & Trends")

    # Display formatted table
    st.dataframe(filtered_data.style.set_properties(**{'text-align': 'left'}).set_table_styles(
        [{'selector': 'thead th', 'props': [('font-size', '14px'), ('background-color', '#3498db'), ('color', 'white')]}]
    ), height=400)

    # Trend Chart for Selected Particulars
    if "All" not in particulars_selected and not filtered_data.empty:
        fig = px.line(filtered_data, x="Month", y="Rs", 
                      title=f"📈 Trend for {', '.join(particulars_selected)}", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# --- NPA Trends ---
st.header("📉 NPA Trends")

# Validate NPA Data Columns
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

