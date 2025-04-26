import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from datetime import datetime

# ---------------------- Data Loading ----------------------

@st.cache_data
def fetch_excel_from_github(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"

try:
    excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
    xls = pd.ExcelFile(BytesIO(excel_bytes))
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

# ---------------------- Data Parsing ----------------------

try:
    data = xls.parse("Data").drop(
        columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"],
        errors="ignore"
    )
    npa_data = xls.parse("Sheet1")
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# ---------------------- Formatting Helpers ----------------------

def format_label(value, is_percentage=False):
    if isinstance(value, (int, float)):
        if is_percentage or (abs(value) < 1 and value != 0):
            return f"{value * 100:.2f}%"
        return f"{value:,.0f}"
    return value

def format_dataframe(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['float', 'int']):
        is_percentage = any(s in col.lower() for s in ["npa", "to", "advance", "rs"])
        df_copy[col] = df_copy[col].apply(lambda x: format_label(x, is_percentage))
    return df_copy

def apply_data_labels(fig, column_data, is_percentage=False):
    labels = [format_label(v, is_percentage) for v in column_data]
    fig.update_traces(text=labels, textposition="top center", mode="lines+text")

def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(240, 248, 255, 0.85)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_font=dict(size=18, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        xaxis_title_font=dict(size=14, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        yaxis_title_font=dict(size=14, color="rgb(32, 64, 128)", family="Arial, sans-serif"),
        title_x=0.5,
        xaxis=dict(tickfont=dict(size=12, color="rgb(32, 64, 128)")),
        yaxis=dict(tickfont=dict(size=12, color="rgb(32, 64, 128)")),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    return fig

# ---------------------- Dashboard Layout ----------------------

st.title("📊 Financial Dashboard")

tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

# ---------------------- Tab 1: Financial Data ----------------------

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
            "Select Particulars:",
            ["All"] + list(data["Particulars"].dropna().unique()),
            default=st.session_state["particulars_selected"]
        )

        month_selected = st.multiselect(
            "Select Month:",
            ["All"] + list(data["Month"].dropna().unique()),
            default=st.session_state["month_selected"]
        )

        if st.button("🔄 Reset Filters"):
            st.session_state["particulars_selected"] = ["All"]
            st.session_state["month_selected"] = ["All"]
            st.experimental_rerun()

        # Apply filters
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
            st.warning("⚠️ No data available for the selected filters! Try adjusting your choices.")
        else:
            styled_data = format_dataframe(filtered_data)
            st.dataframe(styled_data, height=400)

            if "All" not in particulars_selected:
                show_data_labels = st.checkbox("📊 Show Data Labels", key="show_labels_financial")
                title = ", ".join(particulars_selected)

                fig = px.line(
                    filtered_data,
                    x="Month",
                    y="Rs",
                    title=f"📈 {title}",
                    template="plotly_white",
                    markers=True
                )

                if show_data_labels:
                    apply_data_labels(fig, filtered_data["Rs"])

                fig.update_yaxes(tickformat=".2f")
                fig.update_layout(width=1200, height=600)
                fig = style_chart(fig)
                st.plotly_chart(fig, use_container_width=True)

# ---------------------- Tab 2: NPA Trends ----------------------

with tab2:
    st.header("📉 NPA Trends")

    required_cols = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}

    if required_cols.issubset(npa_data.columns):

        col1, col2 = st.columns(2)

        with col1:
            show_gross_labels = st.checkbox("📊 Show Data Labels", key="show_labels_gross_npa")

            fig1 = px.line(
                npa_data,
                x="Month",
                y="Gross Npa To Gross Advances",
                title="📊 Gross NPA Trend",
                template="plotly_white",
                markers=True
            )

            if show_gross_labels:
                apply_data_labels(fig1, npa_data["Gross Npa To Gross Advances"], is_percentage=True)

            fig1.update_yaxes(tickformat=".2%")
            fig1.update_layout(width=1200, height=600)
            fig1 = style_chart(fig1)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            show_net_labels = st.checkbox("📊 Show Data Labels", key="show_labels_net_npa")

            fig2 = px.line(
                npa_data,
                x="Month",
                y="Net Npa To Net Advances",
                title="📊 Net NPA Trend",
                template="plotly_white",
                markers=True
            )

            if show_net_labels:
                apply_data_labels(fig2, npa_data["Net Npa To Net Advances"], is_percentage=True)

            fig2.update_yaxes(tickformat=".2%")
            fig2.update_layout(width=1200, height=600)
            fig2 = style_chart(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        show_bar_labels = st.checkbox("📊 Show Data Labels", key="show_labels_bar_npa")

        fig3 = px.bar(
            npa_data,
            x="Month",
            y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"],
            barmode="group",
            title="📊 Gross vs. Net NPA",
            template="plotly_white"
        )

        if show_bar_labels:
            fig3.update_traces(texttemplate="%{y:.2%}", textposition="outside")

        fig3.update_yaxes(tickformat=".2%")
        fig3.update_layout(width=1200, height=600)
        fig3 = style_chart(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.error("⚠️ NPA data is missing required columns!")
