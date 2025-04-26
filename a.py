import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import BytesIO
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional blue theme
st.markdown("""
<style>
    /* Main theme colors - professional blue palette */
    :root {
        --primary-color: #1E3A8A;
        --secondary-color: #3B82F6;
        --accent-color: #93C5FD;
        --background-color: #F1F5F9;
        --text-color: #1E293B;
        --light-text: #64748B;
    }
    
    /* Main container styling */
    .main {
        background-color: var(--background-color);
        padding: 2rem;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: var(--primary-color) !important;
        font-family: 'Arial', sans-serif;
        font-weight: 700;
    }
    
    h1 {
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--secondary-color);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-color);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Multiselect styling */
    .stMultiSelect > div {
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px 5px 0 0;
        color: var(--light-text);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--secondary-color) !important;
        color: white !important;
    }
    
    /* Card-like containers */
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: var(--primary-color);
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Function to create card-like containers
def card_container(title, content_function):
    st.markdown(f'<div class="card"><h3>{title}</h3>', unsafe_allow_html=True)
    content_function()
    st.markdown('</div>', unsafe_allow_html=True)

# Function to fetch Excel file from GitHub
@st.cache_data
def fetch_excel_from_github(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

# Load Excel file from GitHub
GITHUB_FILE_URL = "https://github.com/sudbrl/baselreport/raw/main/baseldata.xlsx"
try:
    with st.spinner("📊 Loading financial data..."):
        excel_bytes = fetch_excel_from_github(GITHUB_FILE_URL)
        xls = pd.ExcelFile(BytesIO(excel_bytes)) 
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Failed to load data from GitHub! Error: {e}")
    st.stop()

# Parse "Data" and "Sheet1" (NPA Data)
try:
    data = xls.parse("Data").drop(columns=["Helper", "Unnamed: 7", "Unnamed: 8", "Rs.1", "Rs.2", "Movements(%)"], errors="ignore")
    npa_data = xls.parse("Sheet1")
except Exception as e:
    st.error(f"⚠️ Error parsing Excel sheets: {e}")
    st.stop()

# Function to format values for display
def format_label(value, is_percentage=False):
    if isinstance(value, (int, float)):
        if is_percentage:
            return f"{value * 100:.2f}%"  # Format as percentage
        elif abs(value) < 1 and value != 0:
            return f"{value * 100:.2f}%"  # Format as percentage
        return f"{value:,.0f}"  # Format large numbers with commas
    return value  

# Function to apply formatting to dataframe
def format_dataframe(df):
    df_copy = df.copy()
    
    # Identify which columns are percentages (e.g., columns containing the word 'Npa' or 'Rs')
    for col in df_copy.select_dtypes(include=['float', 'int']):
        # Add custom condition to identify percentage columns
        is_percentage = any(substring in col.lower() for substring in ["npa", "to", "advance", "rs"])  # Adjust as needed
        df_copy[col] = df_copy[col].apply(lambda x: format_label(x, is_percentage))
    return df_copy

# Function to apply formatted data labels to charts
def apply_data_labels(fig, column_data, is_percentage=False):
    formatted_labels = [format_label(v, is_percentage) for v in column_data]
    fig.update_traces(text=formatted_labels, textposition="top center", mode="lines+text")

# Enhanced function to apply professional blue styling to the charts
def style_chart(fig, chart_type="line"):
    # Professional blue color palette
    colors = {
        'primary': '#1E3A8A',      # Dark blue
        'secondary': '#3B82F6',    # Medium blue
        'accent': '#93C5FD',       # Light blue
        'highlight': '#2563EB',    # Bright blue
        'background': '#F1F5F9',   # Light gray-blue
        'grid': '#E2E8F0',         # Lighter gray
        'text': '#1E293B'          # Dark text
    }
    
    # Set the background colors and styling
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        title_font=dict(size=20, color=colors['primary'], family="Arial, sans-serif", weight='bold'),
        xaxis_title_font=dict(size=14, color=colors['text'], family="Arial, sans-serif"),
        yaxis_title_font=dict(size=14, color=colors['text'], family="Arial, sans-serif"),
        title_x=0.5,  # Center align the title
        xaxis=dict(
            tickfont=dict(size=12, color=colors['text']),
            gridcolor=colors['grid'],
            showgrid=True,
            zeroline=False,
            showline=True,
            linecolor=colors['grid'],
        ),
        yaxis=dict(
            tickfont=dict(size=12, color=colors['text']),
            gridcolor=colors['grid'],
            showgrid=True,
            zeroline=False,
            showline=True,
            linecolor=colors['grid'],
        ),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins
        legend=dict(
            font=dict(size=12, color=colors['text']),
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor=colors['grid'],
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
    )
    
    # Apply specific styling based on chart type
    if chart_type == "line":
        # For line charts, add shadow and make lines thicker
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8, line=dict(width=2, color='white')),
        )
        
        # Add subtle shadow to lines
        for trace in fig.data:
            if hasattr(trace, 'line'):
                trace.line.shadow = True
    
    elif chart_type == "bar":
        # For bar charts, add gradient and borders
        fig.update_traces(
            marker_line_color=colors['primary'],
            marker_line_width=1,
            opacity=0.85
        )
    
    # Add subtle grid pattern
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=colors['grid'],
        tickangle=-45
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=colors['grid']
    )
    
    return fig

# Dashboard Header with Logo and Title
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <div style="font-size: 3rem; margin-right: 1rem;">📊</div>
    <div>
        <h1 style="margin-bottom: 0;">Financial Dashboard</h1>
        <p style="color: #64748B; margin-top: 0;">Comprehensive financial data analysis and visualization</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Last updated timestamp
st.markdown(f"<p style='text-align: right; color: #64748B; font-size: 0.8rem;'>Last updated: {datetime.now().strftime('%B %d, %Y %H:%M')}</p>", unsafe_allow_html=True)

# Tabs with enhanced styling
tab1, tab2 = st.tabs(["📜 Financial Data", "📉 NPA Trends"])

### --- Financial Data Tab ---
with tab1:
    st.header("📜 Financial Data Overview")
    st.markdown("<p style='color: #64748B; margin-bottom: 2rem;'>Analyze and visualize key financial metrics and trends</p>", unsafe_allow_html=True)

    col_filters, col_content = st.columns([1, 3])

    with col_filters:
        card_container("🔍 Filters", lambda: filter_section())
        
        def filter_section():
            if "particulars_selected" not in st.session_state:
                st.session_state["particulars_selected"] = ["All"]
            if "month_selected" not in st.session_state:
                st.session_state["month_selected"] = ["All"]

            particulars_selected = st.multiselect(
                "Select Particulars:", ["All"] + list(data["Particulars"].dropna().unique()), 
                default=st.session_state["particulars_selected"]
            )
            month_selected = st.multiselect(
                "Select Month:", ["All"] + list(data["Month"].dropna().unique()), 
                default=st.session_state["month_selected"]
            )

            if st.button("🔄 Reset Filters"):
                st.session_state["particulars_selected"] = ["All"]
                st.session_state["month_selected"] = ["All"]
                st.experimental_rerun()

            # Apply Filters
            filtered_data = data.copy()
            if "All" not in particulars_selected:
                filtered_data = filtered_data[filtered_data["Particulars"].isin(particulars_selected)]
            if "All" not in month_selected:
                filtered_data = filtered_data[filtered_data["Month"].isin(month_selected)]

            csv_data = filtered_data.to_csv(index=False).encode("utf-8")
            file_name = f"filtered_financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            st.download_button("📥 Download Filtered Data", data=csv_data, file_name=file_name, mime="text/csv")
            
            return filtered_data
        
        filtered_data = filter_section()

    with col_content:
        if filtered_data.empty:
            st.warning("⚠️ No data available for the selected filters! Try adjusting your choices.")
        else:
            # Data Table Card
            card_container("📊 Data Table", lambda: table_section(filtered_data))
            
            def table_section(df):
                styled_data = format_dataframe(df)
                st.dataframe(styled_data, height=300, use_container_width=True)
            
            # Only show chart if specific particulars are selected
            if "All" not in st.session_state["particulars_selected"]:
                card_container("📈 Financial Trends", lambda: chart_section(filtered_data))
                
                def chart_section(df):
                    show_data_labels = st.checkbox("📊 Show Data Labels", key="show_labels_financial")

                    # Dynamic title with selected "Particulars"
                    selected_particulars_title = ", ".join(st.session_state["particulars_selected"]) if "All" not in st.session_state["particulars_selected"] else "Financial Trend"

                    # Create enhanced line chart with area fill
                    fig = go.Figure()
                    
                    # Add line with area fill
                    fig.add_trace(go.Scatter(
                        x=df["Month"], 
                        y=df["Rs"],
                        mode='lines+markers',
                        name=selected_particulars_title,
                        line=dict(color='#3B82F6', width=3),
                        marker=dict(size=10, color='#1E3A8A', line=dict(width=2, color='white')),
                        fill='tozeroy',
                        fillcolor='rgba(147, 197, 253, 0.3)'
                    ))
                    
                    # Add data labels if requested
                    if show_data_labels:
                        fig.update_traces(
                            text=[f"{x:,.0f}" for x in df["Rs"]],
                            textposition="top center",
                            textfont=dict(size=12, color='#1E3A8A')
                        )
                    
                    # Set chart title and axes
                    fig.update_layout(
                        title=f"📈 {selected_particulars_title}",
                        xaxis_title="Month",
                        yaxis_title="Value (Rs)",
                        height=500
                    )
                    
                    # Apply professional styling
                    fig = style_chart(fig, "line")
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)

### --- NPA Trends Tab ---
with tab2:
    st.header("📉 NPA Trends")
    st.markdown("<p style='color: #64748B; margin-bottom: 2rem;'>Monitor and analyze Non-Performing Asset trends over time</p>", unsafe_allow_html=True)

    required_npa_columns = {"Month", "Gross Npa To Gross Advances", "Net Npa To Net Advances"}
    if required_npa_columns.issubset(npa_data.columns):
        # Summary metrics
        st.markdown("<h3>📌 Key Metrics</h3>", unsafe_allow_html=True)
        
        metric_cols = st.columns(4)
        
        # Calculate latest metrics
        latest_month = npa_data["Month"].iloc[-1]
        latest_gross = npa_data["Gross Npa To Gross Advances"].iloc[-1]
        latest_net = npa_data["Net Npa To Net Advances"].iloc[-1]
        
        # Calculate changes from previous month
        if len(npa_data) > 1:
            prev_gross = npa_data["Gross Npa To Gross Advances"].iloc[-2]
            prev_net = npa_data["Net Npa To Net Advances"].iloc[-2]
            gross_change = (latest_gross - prev_gross) / prev_gross
            net_change = (latest_net - prev_net) / prev_net
        else:
            gross_change = 0
            net_change = 0
        
        # Display metrics with custom styling
        with metric_cols[0]:
            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <p style="color: #64748B; margin-bottom: 0.5rem; font-size: 0.9rem;">Latest Month</p>
                <h2 style="color: #1E3A8A; margin: 0;">{latest_month}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_cols[1]:
            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <p style="color: #64748B; margin-bottom: 0.5rem; font-size: 0.9rem;">Gross NPA Ratio</p>
                <h2 style="color: #1E3A8A; margin: 0;">{latest_gross:.2%}</h2>
                <p style="color: {'#10B981' if gross_change <= 0 else '#EF4444'}; margin: 0; font-size: 0.9rem;">
                    {gross_change:.2%} {'▼' if gross_change <= 0 else '▲'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_cols[2]:
            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <p style="color: #64748B; margin-bottom: 0.5rem; font-size: 0.9rem;">Net NPA Ratio</p>
                <h2 style="color: #1E3A8A; margin: 0;">{latest_net:.2%}</h2>
                <p style="color: {'#10B981' if net_change <= 0 else '#EF4444'}; margin: 0; font-size: 0.9rem;">
                    {net_change:.2%} {'▼' if net_change <= 0 else '▲'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_cols[3]:
            # Calculate the difference between gross and net
            difference = latest_gross - latest_net
            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <p style="color: #64748B; margin-bottom: 0.5rem; font-size: 0.9rem;">Provision Coverage</p>
                <h2 style="color: #1E3A8A; margin: 0;">{difference:.2%}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Trend charts
        st.markdown("<h3>📊 Trend Analysis</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)

        with col1:
            card_container("Gross NPA Trend", lambda: gross_npa_chart())
            
            def gross_npa_chart():
                show_data_labels_gross = st.checkbox("📊 Show Data Labels", key="show_labels_gross_npa")

                # Create enhanced line chart with area fill for Gross NPA
                fig1 = go.Figure()
                
                fig1.add_trace(go.Scatter(
                    x=npa_data["Month"], 
                    y=npa_data["Gross Npa To Gross Advances"],
                    mode='lines+markers',
                    name='Gross NPA',
                    line=dict(color='#3B82F6', width=3),
                    marker=dict(size=10, color='#1E3A8A', line=dict(width=2, color='white')),
                    fill='tozeroy',
                    fillcolor='rgba(147, 197, 253, 0.3)'
                ))
                
                if show_data_labels_gross:
                    fig1.update_traces(
                        text=[f"{x:.2%}" for x in npa_data["Gross Npa To Gross Advances"]],
                        textposition="top center",
                        textfont=dict(size=12, color='#1E3A8A')
                    )
                
                fig1.update_layout(
                    title="📊 Gross NPA to Gross Advances",
                    xaxis_title="Month",
                    yaxis_title="Ratio",
                    height=400
                )
                
                fig1.update_yaxes(tickformat=".2%")  # Format as percentage
                fig1 = style_chart(fig1, "line")
                
                st.plotly_chart(fig1, use_container_width=True)

        with col2:
            card_container("Net NPA Trend", lambda: net_npa_chart())
            
            def net_npa_chart():
                show_data_labels_net = st.checkbox("📊 Show Data Labels", key="show_labels_net_npa")

                # Create enhanced line chart with area fill for Net NPA
                fig2 = go.Figure()
                
                fig2.add_trace(go.Scatter(
                    x=npa_data["Month"], 
                    y=npa_data["Net Npa To Net Advances"],
                    mode='lines+markers',
                    name='Net NPA',
                    line=dict(color='#3B82F6', width=3),
                    marker=dict(size=10, color='#1E3A8A', line=dict(width=2, color='white')),
                    fill='tozeroy',
                    fillcolor='rgba(147, 197, 253, 0.3)'
                ))
                
                if show_data_labels_net:
                    fig2.update_traces(
                        text=[f"{x:.2%}" for x in npa_data["Net Npa To Net Advances"]],
                        textposition="top center",
                        textfont=dict(size=12, color='#1E3A8A')
                    )
                
                fig2.update_layout(
                    title="📊 Net NPA to Net Advances",
                    xaxis_title="Month",
                    yaxis_title="Ratio",
                    height=400
                )
                
                fig2.update_yaxes(tickformat=".2%")  # Format as percentage
                fig2 = style_chart(fig2, "line")
                
                st.plotly_chart(fig2, use_container_width=True)

        # Comparison chart
        card_container("Gross vs. Net NPA Comparison", lambda: comparison_chart())
        
        def comparison_chart():
            show_data_labels_bar = st.checkbox("📊 Show Data Labels", key="show_labels_bar_npa")

            # Create enhanced bar chart for comparison
            fig3 = go.Figure()
            
            # Add Gross NPA bars
            fig3.add_trace(go.Bar(
                x=npa_data["Month"],
                y=npa_data["Gross Npa To Gross Advances"],
                name='Gross NPA',
                marker_color='#3B82F6',
                opacity=0.85
            ))
            
            # Add Net NPA bars
            fig3.add_trace(go.Bar(
                x=npa_data["Month"],
                y=npa_data["Net Npa To Net Advances"],
                name='Net NPA',
                marker_color='#93C5FD',
                opacity=0.85
            ))
            
            if show_data_labels_bar:
                fig3.update_traces(
                    texttemplate='%{y:.2%}',
                    textposition='outside',
                    textfont=dict(size=12, color='#1E3A8A')
                )
            
            fig3.update_layout(
                title="📊 Gross vs. Net NPA Comparison",
                xaxis_title="Month",
                yaxis_title="Ratio",
                barmode='group',
                height=500
            )
            
            fig3.update_yaxes(tickformat=".2%")  # Format as percentage
            fig3 = style_chart(fig3, "bar")
            
            st.plotly_chart(fig3, use_container_width=True)

    else:
        st.error("⚠️ NPA data is missing required columns!")
