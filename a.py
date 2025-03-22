import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# ✅ Set Page Configuration
st.set_page_config(layout="wide", page_title="Financial Dashboard")

# ✅ Load Data from GitHub
@st.cache_data
def load_data():
    url = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsm"
    response = requests.get(url)
    
    if response.status_code == 200:
        file_bytes = io.BytesIO(response.content)
        xls = pd.ExcelFile(file_bytes)
        return xls
    else:
        st.error("❌ Failed to load data from GitHub. Please check the file URL.")
        return None

xls = load_data()

if xls is not None:
    # ✅ Parse "Data" Sheet
    raw_data = xls.parse("Data")
    columns_to_drop = ["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"]
    data = raw_data.drop(columns=[col for col in columns_to_drop if col in raw_data.columns])

    # ✅ Parse "NPA Data" Sheet
    npa_data = xls.parse("Sheet1")

    # ✅ Initialize Session State for Filters
    if "particulars_selected" not in st.session_state:
        st.session_state["particulars_selected"] = ["All"]
    if "month_selected" not in st.session_state:
        st.session_state["month_selected"] = ["All"]

    # ✅ UI Layout: Filters on Left, Data on Right
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔍 Filters")

        # 🎯 Particulars Filter
        particulars_options = ["All"] + list(data["Particulars"].dropna().unique())
        selected_particulars = st.multiselect("Select Particulars:", particulars_options, 
                                              default=st.session_state["particulars_selected"])
        
        # Ensure "All" is removed if other options are selected
        if "All" in selected_particulars and len(selected_particulars) > 1:
            selected_particulars.remove("All")

        # 🎯 Month Filter
        month_options = ["All"] + list(data["Month"].dropna().unique())
        selected_months = st.multiselect("Select Month:", month_options, 
                                         default=st.session_state["month_selected"])

        # Ensure "All" is removed if other options are selected
        if "All" in selected_months and len(selected_months) > 1:
            selected_months.remove("All")

        # 🔄 Reset Button
        if st.button("♻️ Reset Filters", use_container_width=True):
            st.session_state["particulars_selected"] = ["All"]
            st.session_state["month_selected"] = ["All"]
            st.experimental_rerun()

        # 📥 Download Button (Small & Stylish)
        def convert_df_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Filtered Data")
            processed_data = output.getvalue()
            return processed_data

        if not data.empty:
            filtered_excel = convert_df_to_excel(data)
            st.download_button(
                label="📥 Download Data",
                data=filtered_excel,
                file_name="filtered_financial_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_button",
                help="Download the filtered data in Excel format.",
                use_container_width=True
            )

    # ✅ Data Table on Right (Always Visible)
    with col2:
        st.subheader("📊 Filtered Financial Data")

        # 🔎 Apply Filters
        filtered_data = data.copy()
        if selected_particulars and "All" not in selected_particulars:
            filtered_data = filtered_data[filtered_data["Particulars"].isin(selected_particulars)]
        if selected_months and "All" not in selected_months:
            filtered_data = filtered_data[filtered_data["Month"].isin(selected_months)]

        # 🎨 Styled Data Table
        if not filtered_data.empty:
            styled_table = filtered_data.style.set_properties(**{
                'background-color': '#F8F9FA',
                'border': '1px solid #dee2e6',
                'text-align': 'left'
            }).set_table_styles([
                {'selector': 'thead th', 'props': [('background-color', '#007BFF'), 
                                                    ('color', 'white'), ('text-align', 'center')]},
                {'selector': 'tbody td', 'props': [('border', '1px solid #dee2e6')]}
            ])
            st.dataframe(filtered_data, height=400)
            
            # 📈 Line Chart if Only One Particular is Selected
            if len(selected_particulars) == 1 and "All" not in selected_particulars:
                fig = px.line(filtered_data, x="Month", y="Rs", 
                              title=f"📈 Trend for {selected_particulars[0]}", 
                              template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")

    # ✅ NPA Trends Section (Separate Tab)
    st.markdown("---")  # Separator
    st.subheader("📊 NPA Trends")

    if {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}.issubset(npa_data.columns):
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(npa_data, x="Month", y="Gross Npa To Gross Advances",
                           title="📉 Gross NPA To Gross Advances Trend", template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(npa_data, x="Month", y="Net Npa To Net Advances",
                           title="📊 Net NPA To Net Advances Trend", template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

        # 📊 Bar Chart for NPA Comparison
        fig3 = px.bar(npa_data, x="Month", y=["Gross Npa To Gross Advances", "Net Npa To Net Advances"],
                      barmode='group', title="📊 Comparison of Gross & Net NPA", template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error("🚨 NPA data is missing required columns!")

