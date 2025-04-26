import streamlit as st
import pandas as pd

# Set up the page
st.set_page_config(page_title="Basel Report Viewer", layout="wide")

# Load the Excel file from GitHub
@st.cache_data
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    return pd.read_excel(url)

df = load_data()

# App title
st.title("📊 Basel Report Data Viewer")

# Show dataframe
st.dataframe(df)

# Optional: Add filters
with st.expander("🔍 Filter Data"):
    columns = df.columns.tolist()
    selected_column = st.selectbox("Select column to filter", columns)
    unique_values = df[selected_column].dropna().unique()
    selected_value = st.selectbox("Select value", unique_values)
    filtered_df = df[df[selected_column] == selected_value]
    st.write("Filtered Data:")
    st.dataframe(filtered_df)
