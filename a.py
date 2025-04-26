import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from datetime import datetime

# Column mappings for flexibility
COLUMN_MAPPING = {
    "month": "Month",
    "particulars": "Particulars",
    "financial_value": "Rs",
    "gross_npa": "Gross Npa To Gross Advances",
    "net_npa": "Net Npa To Net Advances"
}

# Function to fetch Excel file from GitHub
@st.cache_data
def fetch_excel_from_github(url):
    with st.spinner("Fetching data from GitHub..."):
        response = requests.get(url)
        response.raise_for_status()
        return response.content

# Function to validate required columns
def validate_columns(df, required_cols, sheet_name):
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"⚠️ Missing required columns in {sheet_name}: {', '.join(missing_cols)}")
        st.stop()
    return True

# Function to clean numeric column
def clean_numeric_column(series):
    # Convert to string to handle mixed types
    series = series.astype(str)
    # Remove common formatting (commas, currency symbols, spaces)
    series = series.str.replace(r'[,\$\s]', '', regex=True)
    # Replace common non-numeric values with NaN
    series = series.replace(['', 'N/A', 'NA', 'Not Available', 'nan', 'NaN'], pd.NA)
    # Convert to numeric, coercing errors to NaN
    cleaned_series = pd.to_numeric(series, errors='coerce')
    # Report non-numeric values
    non_numeric = series[cleaned_series.isna() & ~series.isna()]
    if not non_numeric.empty:
        st.warning(f"⚠️ Found {len(non_numeric)} non-numeric values in '{series.name}' column. Converted to NaN. Examples: {non_numeric.unique()[:5]}")
    return cleaned_series

# Function to detect percentage columns
def is_percentage_column(series):
    if pd.api.types.is_numeric_dtype(series):
        valid_values = series.dropna()
        if len(valid_values) > 0:
            return valid_values.abs().le(1.5).all()  # Allow small errors (e.g., 1.01)
    return False

# Function to format values to match Excel (percentages as 0.00%, numbers with commas)
def format_label(value, is_percentage=False):
    if pd.isna(value):
        return ""
    if isinstance(value, (int, float)):
        if is_percentage:
            return f"{value * 100:.2f}%"  # Match Excel's 0.00% format
        return f"{value:,.0f}"  # Match Excel's comma-separated format
    return str(value)

# Function to apply formatting to dataframe
def format_dataframe(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['float', 'int']).columns:
        is_percentage = is_percentage_column(df_copy[col])
        df_copy[col] = df_copy[col].apply(lambda x: format_label(x, is_percentage))
    return df_copy

# Function to apply formatted data labels to charts
def apply_data_labels(fig, column_data, is_percentage=False):
    formatted_labels = [format_label(v, is_percentage) for v in column_data]
    fig.update_traces(text=formatted_labels, textposition="top center", mode="lines+text")

# Function to apply fancy styling to charts
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(240, 248, 255, 0.85)',  # Soft light blue background
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
        title_font=dict(size=18, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        xaxis_title_font=dict(size=14, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        yaxis_title_font=dict(size=14, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        title_x=0.5,  # Center title
        xaxis=dict(tickfont=dict(size=12, color="rgb(32, 64, 128)")),
        yaxis=dict(tickfont=dict(size=12, color="rgb(32, 64, 128)")),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

# Cache filtered data
@st.cache_data
def load_and_filter_data(particulars, months, data):
    filtered_data = data.copy()
    if "All" not in particulars:
        filtered_data = filtered_data[filtered_data[COLUMN_MAPPING["particulars"]].isin(particulars)]
    if "All" not in months:
        filtered_data = filtered_data[filtered_data[COLUMN_MAPPING["month"]].isin(months)]
    return filtered_data

# Dashboard Title
st.title("📊 Financial Dashboard")

# Load Excel file from GitHub
GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes))
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

# Parse "Data" and "Sheet1" (NPA Data)
try:
    data = xls.parse("Data", na_values=['N/A', 'NA', 'Not Available']).drop(
        columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore"
    )
    npa_data = xls.parse("Sheet1", na_values=['N/A', 'NA', 'Not Available'])
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# Validate columns
validate_columns(data, [COLUMN_MAPPING["month"], COLUMN_MAPPING["particulars"], COLUMN_MAPPING["financial_value"]], "Data sheet")
validate_columns(npa_data, [COLUMN_MAPPING["month"], COLUMN_MAPPING["gross_npa"], COLUMN_MAPPING["net_npa"]], "NPA sheet")

# Clean numeric columns
data[COLUMN_MAPPING["financial_value"]] = clean_numeric_column(data[COLUMN_MAPPING["financial_value"]])
npa_data[COLUMN_MAPPING["gross_npa"]] = clean_numeric_column(npa_data[COLUMN_MAPPING["gross_npa"]])
npa_data[COLUMN_MAPPING["net_npa"]] = clean_numeric_column(npa_data[COLUMN_MAPPING["net_npa"]])

# Check if Rs column is entirely NaN after cleaning
if data[COLUMN_MAPPING["financial_value"]].isna().all():
    st.error(f"⚠️ Column '{COLUMN_MAPPING['financial_value']}' contains no valid numeric data after cleaning!")
    st.stop()

# Tabs
tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("📜 Financial Data Overview")

    col_filters, col_content = st.columns([1, 3])

    with col_filters:
        st.subheader("🔍 Filters")

        if "particulars_selected" not in st.session_state:
            st.session_state["particulars_selected"] = ["All"]
        if "month_selected" not in st.session_state:
            st.session_state["month_selected"] = ["All"]

        particulars_selected = st.multiselect(
            "Select Particulars:", ["All"] + list(data[COLUMN_MAPPING["particulars"]].dropna().unique()),
            default=st.session_state["particulars_selected"]
        )
        month_selected = st.multiselect(
            "Select Month:", ["All"] + list(data[COLUMN_MAPPING["month"]].dropna().unique()),
            default=st.session_state["month_selected"]
        )

        if st.button("🔄 Reset Filters"):
            st.session_state["particulars_selected"] = ["All"]
            st.session_state["month_selected"] = ["All"]
            st.rerun()

        # Apply Filters
        filtered_data = load_and_filter_data(particulars_selected, month_selected, data)

        csv_data = filtered_data.to_csv(index=False).encode("utf-8")
        file_name = f"filtered_financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button("📥 Download Filtered Data", data=csv_data, file_name=file_name, mime="text/csv")

    with col_content:
        st.subheader("📊 Data Table & Trends")

        if filtered_data.empty:
            st.warning("⚠️ No data available for the selected filters! Try adjusting your choices.")
        else:
            styled_data = format_dataframe(filtered_data)
            st.dataframe(styled_data, height=400)

            if "All" not in particulars_selected:
                show_data_labels = st.checkbox("📊 Show Data Labels", key="show_labels_financial")

                # Dynamic title
                selected_particulars_title = ", ".join(particulars_selected) if "All" not in particulars_selected else "Financial Trend"

                fig = px.line(filtered_data, x=COLUMN_MAPPING["month"], y=COLUMN_MAPPING["financial_value"],
                              title=f"📈 {selected_particulars_title}", template="plotly_white", markers=True)
                if show_data_labels:
                    apply_data_labels(fig, filtered_data[COLUMN_MAPPING["financial_value"]])
                fig.update_yaxes(tickformat=",")  # Comma-separated numbers
                fig = style_chart(fig)
                st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")

    col1, col2 = st.columns(2)

    with col1:
        show_data_labels_gross = st.checkbox("📊 Show Data Labels", key="show_labels_gross_npa")

        fig1 = px.line(npa_data, x=COLUMN_MAPPING["month"], y=COLUMN_MAPPING["gross_npa"],
                       title="📊 Gross NPA Trend", template="plotly_white", markers=True)
        if show_data_labels_gross:
            apply_data_labels(fig1, npa_data[COLUMN_MAPPING["gross_npa"]], is_percentage=True)
        fig1.update_yaxes(tickformat=".2%")  # Match Excel's 0.00% format
        fig1 = style_chart(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        show_data_labels_net = st.checkbox("📊 Show Data Labels", key="show_labels_net_npa")

        fig2 = px.line(npa_data, x=COLUMN_MAPPING["month"], y=COLUMN_MAPPING["net_npa"],
                       title="📊 Net NPA Trend", template="plotly_white", markers=True)
        if show_data_labels_net:
            apply_data_labels(fig2, npa_data[COLUMN_MAPPING["net_npa"]], is_percentage=True)
        fig2.update_yaxes(tickformat=".2%")  # Match Excel's 0.00% format
        fig2 = style_chart(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    show_data_labels_bar = st.checkbox("📊 Show Data Labels", key="show_labels_bar_npa")

    fig3 = px.bar(npa_data, x=COLUMN_MAPPING["month"], y=[COLUMN_MAPPING["gross_npa"], COLUMN_MAPPING["net_npa"]],
                  barmode='group', title="📊 Gross vs. Net NPA", template="plotly_white")
    if show_data_labels_bar:
        fig3.update_traces(texttemplate="%{y:.2%}", textposition="outside")
    fig3.update_yaxes(tickformat=".2%")  # Match Excel's 0.00% format
    fig3 = style_chart(fig3)
    st.plotly_chart(fig3, use_container_width=True)
