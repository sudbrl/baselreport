import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from datetime import datetime

# Function to load Excel file
@st.cache_data
def load_excel(file):
    return pd.ExcelFile(file)

# Load uploaded Excel file
file_path = "./baseldata.xlsx"  # Update as needed
xls = load_excel(file_path)

# Parse "Data" and "Sheet1" (NPA Data)
data = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
npa_data = xls.parse("Sheet1")

# Function to detect percentages
def is_percentage_column(particular):
    percentage_keywords = ["Ratio", "NPA", "Advances", "Capital"]
    return any(keyword in particular for keyword in percentage_keywords)

# Format values properly
def format_value(value, particular):
    if isinstance(value, str) and "%" in value:
        return value  # Keep preformatted percentages
    if isinstance(value, (int, float)):
        if is_percentage_column(particular):
            return f"{value * 100:.2f}%"  # Convert decimal to percentage
        return f"{value:,.0f}"  # Format large numbers with commas
    return value

# Format entire dataframe
def format_dataframe(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['float', 'int']):
        df_copy[col] = df_copy.apply(lambda row: format_value(row[col], row['Particulars']), axis=1)
    return df_copy

# Function to apply formatted labels to charts
def apply_data_labels(fig, column_data, particular):
    formatted_labels = [format_value(v, particular) for v in column_data]
    fig.update_traces(text=formatted_labels, textposition="top center", mode="lines+text")

# Dashboard Title
st.title("📊 Financial Dashboard")

tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("📜 Financial Data Overview")
    col_filters, col_content = st.columns([1, 3])

    with col_filters:
        st.subheader("🔍 Filters")
        particulars_selected = st.multiselect("Select Particulars:", ["All"] + list(data["Particulars"].dropna().unique()), default=["All"])
        month_selected = st.multiselect("Select Month:", ["All"] + list(data["Month"].dropna().unique()), default=["All"])
        
        if st.button("🔄 Reset Filters"):
            st.experimental_rerun()
        
        filtered_data = data.copy()
        if "All" not in particulars_selected:
            filtered_data = filtered_data[filtered_data["Particulars"].isin(particulars_selected)]
        if "All" not in month_selected:
            filtered_data = filtered_data[filtered_data["Month"].isin(month_selected)]
        
        csv_data = filtered_data.to_csv(index=False).encode("utf-8")
        file_name = f"filtered_financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button("📥 Download Filtered Data", data=csv_data, file_name=file_name, mime="text/csv")

    with col_content:
        st.subheader("📊 Data Table & Trends")
        
        if filtered_data.empty:
            st.warning("⚠️ No data available for the selected filters!")
        else:
            styled_data = format_dataframe(filtered_data)
            st.dataframe(styled_data, height=400)
            
            if "All" not in particulars_selected:
                show_labels = st.checkbox("📊 Show Data Labels")
                
                for particular in particulars_selected:
                    df_particular = filtered_data[filtered_data["Particulars"] == particular]
                    fig = px.line(df_particular, x="Month", y="Rs", title=f"📈 {particular} Trend", template="plotly_white", markers=True)
                    fig.update_yaxes(title_text="Rs (000)" if not is_percentage_column(particular) else "Percentage", tickformat=".2%" if is_percentage_column(particular) else ",")
                    
                    if show_labels:
                        apply_data_labels(fig, df_particular["Rs"], particular)
                    st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")
    required_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
    
    if required_columns.issubset(npa_data.columns):
        col1, col2 = st.columns(2)
        
        with col1:
            show_labels_gross = st.checkbox("📊 Show Data Labels", key="show_labels_gross")
            fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances", title="📊 Gross NPA Trend", template="plotly_white", markers=True)
            fig1.update_yaxes(title_text="Percentage", tickformat=".2%")
            if show_labels_gross:
                apply_data_labels(fig1, npa_data["Gross Npa To Gross Advances"], "NPA")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            show_labels_net = st.checkbox("📊 Show Data Labels", key="show_labels_net")
            fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances", title="📊 Net NPA Trend", template="plotly_white", markers=True)
            fig2.update_yaxes(title_text="Percentage", tickformat=".2%")
            if show_labels_net:
                apply_data_labels(fig2, npa_data["Net Npa To Net Advances"], "NPA")
            st.plotly_chart(fig2, use_container_width=True)
        
        show_labels_bar = st.checkbox("📊 Show Data Labels", key="show_labels_bar")
        fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"], barmode='group', title="📊 Gross vs. Net NPA", template="plotly_white")
        fig3.update_yaxes(title_text="Percentage", tickformat=".2%")
        if show_labels_bar:
            fig3.update_traces(texttemplate="%{y:.2%}", textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error("⚠️ NPA data is missing required columns!")
