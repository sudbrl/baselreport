import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from io import BytesIO

# Set page configuration to wide mode
st.set_page_config(layout="wide", page_title="Nepal Banking Data Dashboard", 
                  page_icon=":bar_chart:")

# Custom CSS to enhance the appearance
st.markdown("""
<style>
/* You can paste your full CSS here if needed */
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Nepal Banking Data Dashboard")
st.markdown("<p class='medium-font'>Comprehensive analysis of banking data from Nepal</p>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content))

    # Clean data
    df['Rs'] = df['Rs'].replace('-', pd.NA)
    df['Rs'] = pd.to_numeric(df['Rs'], errors='coerce')
    month_order = {month: i for i, month in enumerate(df['Month'].unique())}
    df['Month_Num'] = df['Month'].map(month_order)
    return df

df = load_data()

# Dashboard layout
st.sidebar.header("Filters")

all_particulars = ["All"] + sorted(df['Particulars'].dropna().unique().tolist())
selected_particulars = st.sidebar.multiselect("Select Particulars:", all_particulars, default=["All"])

all_months = ["All"] + sorted(df['Month'].dropna().unique().tolist(), key=lambda x: df[df['Month']==x]['Month_Num'].iloc[0])
selected_months = st.sidebar.multiselect("Select Months:", all_months, default=["All"])

filtered_df = df.copy()
if "All" not in selected_particulars:
    filtered_df = filtered_df[filtered_df['Particulars'].isin(selected_particulars)]
if "All" not in selected_months:
    filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Records", f"{len(filtered_df):,}")
with col2:
    st.metric("Total Amount (Rs)", f"{filtered_df['Rs'].sum():,.2f}")
with col3:
    st.metric("Average Amount (Rs)", f"{filtered_df['Rs'].mean():,.2f}")
with col4:
    st.metric("Unique Particulars", f"{filtered_df['Particulars'].nunique():,}")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)
with col1:
    top_particulars = filtered_df.groupby('Particulars')['Rs'].sum().sort_values(ascending=False).head(10)
    fig1 = px.bar(
        x=top_particulars.index,
        y=top_particulars.values,
        title="Top 10 Particulars by Amount",
        labels={"x": "Particulars", "y": "Total Amount (Rs)"},
        color=top_particulars.values,
        color_continuous_scale=px.colors.sequential.Blues,
        template="plotly_white"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(
        filtered_df,
        x="Rs",
        nbins=50,
        title="Distribution of Amounts",
        labels={"Rs": "Amount (Rs)", "count": "Frequency"},
        color_discrete_sequence=["#1E3A8A"],
        template="plotly_white",
        opacity=0.8,
        marginal="box"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Monthly summary
st.subheader("Monthly Summary")
monthly_summary = filtered_df.groupby('Month')['Rs'].agg(['sum', 'mean', 'count']).reset_index()
monthly_summary.columns = ['Month', 'Total Amount', 'Average Amount', 'Count']
monthly_summary['Total Amount'] = monthly_summary['Total Amount'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
monthly_summary['Average Amount'] = monthly_summary['Average Amount'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
st.dataframe(monthly_summary, use_container_width=True)

# Filtered raw data
st.subheader("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>Nepal Banking Data Analysis Dashboard | Created with Streamlit</p>", unsafe_allow_html=True)
