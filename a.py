import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# Load data
file_path = "Basel Data JBBL (1).xlsm"
xls = pd.ExcelFile(file_path)

# Parse "Data" sheet and filter columns
raw_data = xls.parse("Data")
columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])

# Parse "Sheet1" (NPA Data)
npa_data = xls.parse("Sheet1")

# Apply custom styling to the dashboard
st.markdown(
    """
    <style>
        .main {background-color: #f4f4f9;}
        div.stTitle {color: #2c3e50; text-align: center; font-size: 30px; font-weight: bold;}
        div.block-container {padding: 20px;}
        .stButton button {width: 100%; background-color: #2c3e50; color: white; font-weight: bold; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True
)

# Dashboard Title
st.title("📊 Financial Dashboard")

# Tabs for different datasets
tab1, tab2 = st.tabs(["📈 Financial Data", "📉 NPA Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("Financial Data Overview")

    # Create Two-Column Layout
    left_col, right_col = st.columns([1, 3])

    # Left Column: Filters
    with left_col:
        st.subheader("🔍 Filters")
        
        # Dropdown Filters with "All" and Auto-Remove Logic
        particulars_options = ["All"] + list(data["Particulars"].dropna().unique())
        selected_particulars = st.multiselect("Select Particulars:", particulars_options, default=["All"])

        # Remove "All" if other selections are made
        if "All" in selected_particulars and len(selected_particulars) > 1:
            selected_particulars.remove("All")

        date_options = ["All"] + list(data["Month"].dropna().unique())
        selected_dates = st.multiselect("Select Month:", date_options, default=["All"])

        # Remove "All" if other selections are made
        if "All" in selected_dates and len(selected_dates) > 1:
            selected_dates.remove("All")

        # Reset Button
        if st.button("🔄 Reset Filters"):
            selected_particulars = ["All"]
            selected_dates = ["All"]

    # Apply Filters
    filtered_data = data.copy()
    if "All" not in selected_particulars:
        filtered_data = filtered_data[filtered_data["Particulars"].isin(selected_particulars)]
    if "All" not in selected_dates:
        filtered_data = filtered_data[filtered_data["Month"].isin(selected_dates)]

    # Right Column: Display Data & Charts
    with right_col:
        st.subheader("📊 Data Table & Trends")

        # Display DataFrame
        st.dataframe(filtered_data, height=400)

        # Trend Chart for Selected Particulars
        if "All" not in selected_particulars and selected_particulars:
            fig = px.line(filtered_data, x="Month", y="Rs", color="Particulars",
                          title="📈 Trend of Selected Particulars", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    # Create Two-Column Layout
    left_col, right_col = st.columns([1, 3])

    with right_col:
        # Validate NPA Data Columns
        required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
        if not required_npa_columns.issubset(npa_data.columns):
            st.error("❌ NPA data is missing required columns!")
        else:
            # Create Two Side-by-Side Line Charts
            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", 
                               title="📉 Gross NPA To Gross Advances Trend", template="plotly_white")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", 
                               title="📉 Net NPA To Net Advances Trend", template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)

            # Bar Chart Comparing Gross & Net NPA
            fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], 
                          barmode='group', title="📊 Comparison of Gross & Net NPA", template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
