import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# Apply custom styling
st.markdown(
    """
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        /* Apply font to the entire app */
        html, body, [class*="css"]  {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f2f6;
        }

        /* Title styling */
        .stTitle {
            color: #2c3e50;
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        /* Header styling */
        .stHeader {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }

        /* Dataframe styling */
        .stDataFrame, .stDataEditor {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 2rem;
        }

        /* Plotly chart container */
        .stPlotlyChart {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True
)

# Function to load data with caching and error handling
@st.cache_data
def load_data(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        raw_data = xls.parse("Data")
        columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
        data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])
        npa_data = xls.parse("Sheet1")
        return data, npa_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

# Load data
file_path = "Basel Data.xlsx"
data, npa_data = load_data(file_path)

if data is not None and npa_data is not None:
    # Dashboard Title
    st.title("Financial Dashboard")

    # Tabs for different datasets
    tab1, tab2 = st.tabs(["Financial Data", "Trends"])

    ### --- Financial Data Tab ---
    with tab1:
        st.header("Financial Data Overview")

        # Collapsible Filter Section
        with st.expander("Filter Options", expanded=True):
            # Multiselect Filters with "Select All" Checkboxes
            col1, col2 = st.columns([2, 3])

            with col1:
                # Particulars Filter
                particulars_options = data["Particulars"].dropna().unique().tolist()
                select_all_particulars = st.checkbox("Select All Particulars", value=True)
                if select_all_particulars:
                    selected_particulars = st.multiselect(
                        "Select Particulars:",
                        options=particulars_options,
                        default=particulars_options,
                        disabled=True
                    )
                else:
                    selected_particulars = st.multiselect(
                        "Select Particulars:",
                        options=particulars_options,
                        default=[]
                    )

                # Month Filter
                date_options = data["Month"].dropna().unique().tolist()
                select_all_dates = st.checkbox("Select All Months", value=True)
                if select_all_dates:
                    selected_dates = st.multiselect(
                        "Select Months:",
                        options=date_options,
                        default=date_options,
                        disabled=True
                    )
                else:
                    selected_dates = st.multiselect(
                        "Select Months:",
                        options=date_options,
                        default=[]
                    )

        # Apply Filters
        filtered_data = data[data["Particulars"].isin(selected_particulars) & data["Month"].isin(selected_dates)]

        # Display Editable DataFrame
        st.data_editor(filtered_data, height=400)

        # Trend Chart for Selected Particulars
        if selected_particulars:
            fig = px.line(filtered_data, x="Month", y="Rs", color="Particulars",
                          title="Trend for Selected Particulars", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    ### --- NPA Trends Tab ---
    with tab2:
        st.header("Trends")

        # Validate NPA Data Columns
        required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
        if not required_npa_columns.issubset(npa_data.columns):
            st.error("NPA data is missing required columns!")
        else:
            # Create Two Side-by-Side Line Charts
            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances",
                               title="Gross NPA To Gross Advances Trend", template="plotly_white")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances",
                               title="Net NPA To Net Advances Trend", template="plotly_white")
                st.plotly_chart(fig2, use_container_width=True)

            # Bar Chart Comparing Gross & Net NPA
            fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"],
                          barmode='group', title="Comparison of Gross & Net NPA", template="plotly_white")
            st.plotly_chart(fig3, use_container_width=True)
else:
    st.error("Data could not be loaded. Please check the file path and try again.")
