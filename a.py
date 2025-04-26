import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page configuration to wide mode
st.set_page_config(layout="wide", page_title="Nepal Banking Data Dashboard", 
                  page_icon=":bar_chart:")

# Custom CSS to enhance the appearance
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        background-color: #f5f7f9;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A;
        color: white;
    }
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size: 18px !important;
    }
    .stSidebar {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #FFFFFF;
    }
    .stSidebar .sidebar-content {
        background-color: #FFFFFF;
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 1rem;
        padding-right: 1rem;
    }
    .stSidebar [data-testid="stMarkdownContainer"] h1 {
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E0E0E0;
    }
    .stSidebar [data-testid="stMarkdownContainer"] h3 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    /* Make the dashboard more colorful */
    .positive-value {
        color: #10B981;
        font-weight: bold;
    }
    .negative-value {
        color: #EF4444;
        font-weight: bold;
    }
    /* Enhance table appearance */
    div[data-testid="stTable"] {
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Nepal Banking Data Dashboard")
st.markdown("<p class='medium-font'>Comprehensive analysis of banking data from Nepal</p>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('https://github.com/sudbrl/baselreport/blob/main/baseldata.xlsx')
    
    # Clean data
    # Replace '-' with NaN in Rs column and convert to numeric
    df['Rs'] = df['Rs'].replace('-', pd.NA)
    df['Rs'] = pd.to_numeric(df['Rs'], errors='coerce')
    
    # Create a numeric month column for sorting
    month_order = {month: i for i, month in enumerate(df['Month'].unique())}
    df['Month_Num'] = df['Month'].map(month_order)
    
    return df

# Load the data
df = load_data()

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trend Analysis", "🔍 Detailed Analysis"])

with tab1:
    st.header("Banking Data Overview")
    
    # Sidebar for filtering
    st.sidebar.header("Filters")
    
    # Filter by Particulars
    all_particulars = ["All"] + sorted(df['Particulars'].unique().tolist())
    selected_particulars = st.sidebar.multiselect(
        "Select Particulars:",
        options=all_particulars,
        default=["All"]
    )
    
    # Filter by Month
    all_months = ["All"] + sorted(df['Month'].unique().tolist(), 
                                 key=lambda x: df[df['Month']==x]['Month_Num'].iloc[0] if len(df[df['Month']==x]) > 0 else 0)
    selected_months = st.sidebar.multiselect(
        "Select Months:",
        options=all_months,
        default=["All"]
    )
    
    # Apply filters
    filtered_df = df.copy()
    if "All" not in selected_particulars:
        filtered_df = filtered_df[filtered_df['Particulars'].isin(selected_particulars)]
    if "All" not in selected_months:
        filtered_df = filtered_df[filtered_df['Month'].isin(selected_months)]
    
    # Display key metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Total Records", value=f"{len(filtered_df):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Total Amount (Rs)", 
                 value=f"{filtered_df['Rs'].sum():,.2f}" if not pd.isna(filtered_df['Rs'].sum()) else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Average Amount (Rs)", 
                 value=f"{filtered_df['Rs'].mean():,.2f}" if not pd.isna(filtered_df['Rs'].mean()) else "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Unique Particulars", value=f"{filtered_df['Particulars'].nunique():,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Particulars by Amount
        top_particulars = filtered_df.groupby('Particulars')['Rs'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=top_particulars.index,
            y=top_particulars.values,
            title="Top 10 Particulars by Amount",
            labels={"x": "Particulars", "y": "Total Amount (Rs)"},
            color=top_particulars.values,
            color_continuous_scale=px.colors.sequential.Blues,
            template="plotly_white"
        )
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial, sans-serif", size=12),
            title_font=dict(family="Arial, sans-serif", size=16),
            xaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
            ),
            yaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution of amounts
        fig = px.histogram(
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
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial, sans-serif", size=12),
            title_font=dict(family="Arial, sans-serif", size=16),
            xaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
            ),
            yaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly summary
    st.subheader("Monthly Summary")
    
    monthly_summary = filtered_df.groupby('Month')['Rs'].agg(['sum', 'mean', 'count']).reset_index()
    monthly_summary = monthly_summary.sort_values(by='Month_Num', key=lambda x: filtered_df.loc[filtered_df['Month'].isin(monthly_summary['Month']), 'Month_Num'])
    monthly_summary.columns = ['Month', 'Total Amount', 'Average Amount', 'Count']
    
    # Format the columns
    monthly_summary['Total Amount'] = monthly_summary['Total Amount'].apply(lambda x: f"{x:,.2f}" if not pd.isna(x) else "N/A")
    monthly_summary['Average Amount'] = monthly_summary['Average Amount'].apply(lambda x: f"{x:,.2f}" if not pd.isna(x) else "N/A")
    
    st.dataframe(monthly_summary, use_container_width=True)
    
    # Display the filtered dataframe
    st.subheader("Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)

with tab2:
    st.header("Trend Analysis")
    
    # Get unique months in chronological order
    months = sorted(df['Month'].unique().tolist(), 
                   key=lambda x: df[df['Month']==x]['Month_Num'].iloc[0] if len(df[df['Month']==x]) > 0 else 0)
    
    # Filter by Particulars for trend analysis
    trend_particulars = st.multiselect(
        "Select Particulars for Trend Analysis:",
        options=sorted(df['Particulars'].unique().tolist()),
        default=sorted(df['Particulars'].unique().tolist())[:5]  # Default to first 5
    )
    
    if trend_particulars:
        # Create a pivot table for the trend
        trend_df = df[df['Particulars'].isin(trend_particulars)]
        pivot_df = pd.pivot_table(
            trend_df,
            values='Rs',
            index='Month',
            columns='Particulars',
            aggfunc='sum'
        ).reset_index()
        
        # Reorder months chronologically
        pivot_df['Month_Order'] = pivot_df['Month'].map({m: i for i, m in enumerate(months)})
        pivot_df = pivot_df.sort_values('Month_Order').drop('Month_Order', axis=1)
        
        # Create line chart for trends
        fig = go.Figure()
        
        # Custom color palette
        colors = px.colors.qualitative.Bold
        
        for i, particular in enumerate(trend_particulars):
            if particular in pivot_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=pivot_df['Month'],
                        y=pivot_df[particular],
                        mode='lines+markers',
                        name=particular,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=8, line=dict(width=2, color='white')),
                    )
                )
        
        fig.update_layout(
            title="Trend Analysis by Month",
            xaxis_title="Month",
            yaxis_title="Amount (Rs)",
            height=600,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            ),
            margin=dict(l=20, r=20, t=40, b=100),
            template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial, sans-serif", size=12),
            title_font=dict(family="Arial, sans-serif", size=16),
            xaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
                tickangle=-45
            ),
            yaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
            ),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Month-over-month percentage change
        st.subheader("Month-over-Month Percentage Change")
        
        # Calculate percentage change for each particular
        pct_change_df = pivot_df.copy()
        pct_change_df = pct_change_df.set_index('Month')
        
        for particular in trend_particulars:
            if particular in pct_change_df.columns:
                pct_change_df[f"{particular} % Change"] = pct_change_df[particular].pct_change() * 100
        
        # Select only percentage change columns
        pct_cols = [col for col in pct_change_df.columns if "% Change" in col]
        if pct_cols:
            pct_change_df = pct_change_df[pct_cols].reset_index()
            
            # Create heatmap for percentage changes
            fig = px.imshow(
                pct_change_df.set_index('Month'),
                text_auto='.1f',
                aspect="auto",
                color_continuous_scale=["#FF4B4B", "#FFFFFF", "#10B981"],
                color_continuous_midpoint=0,
                title="Month-over-Month Percentage Change Heatmap"
            )
            fig.update_layout(
                height=500,
                margin=dict(l=20, r=20, t=40, b=20),
                coloraxis_colorbar=dict(
                    title="% Change",
                    thicknessmode="pixels", thickness=20,
                    lenmode="pixels", len=300,
                    yanchor="top", y=1,
                    ticks="outside"
                ),
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(family="Arial, sans-serif", size=16),
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add a summary table of the percentage changes
            st.subheader("Percentage Change Summary")
            
            # Calculate average percentage change for each particular
            avg_pct_change = {}
            for col in pct_cols:
                particular_name = col.replace(" % Change", "")
                avg_pct_change[particular_name] = pct_change_df[col].mean()
            
            # Create a summary dataframe
            summary_df = pd.DataFrame({
                "Particular": list(avg_pct_change.keys()),
                "Average % Change": list(avg_pct_change.values())
            }).sort_values("Average % Change", ascending=False)
            
            # Format the percentage change column
            summary_df["Average % Change"] = summary_df["Average % Change"].apply(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
            
            st.dataframe(summary_df, use_container_width=True)

with tab3:
    st.header("Detailed Analysis")
    
    # Select a specific particular for detailed analysis
    selected_particular = st.selectbox(
        "Select a Particular for Detailed Analysis:",
        options=sorted(df['Particulars'].unique().tolist())
    )
    
    if selected_particular:
        particular_df = df[df['Particulars'] == selected_particular]
        
        # Create two columns for detailed analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Time series for the selected particular
            fig = px.line(
                particular_df.sort_values('Month_Num'),
                x='Month',
                y='Rs',
                markers=True,
                title=f"Time Series for {selected_particular}",
                labels={"Rs": "Amount (Rs)", "Month": "Month"},
                color_discrete_sequence=["#1E3A8A"],
                template="plotly_white"
            )
            
            # Add a trend line
            x_numeric = np.arange(len(particular_df))
            y = particular_df.sort_values('Month_Num')['Rs'].values
            
            # Only add trend line if we have enough data points
            if len(y) > 2:
                z = np.polyfit(x_numeric, y, 1)
                p = np.poly1d(z)
                
                fig.add_trace(
                    go.Scatter(
                        x=particular_df.sort_values('Month_Num')['Month'],
                        y=p(x_numeric),
                        mode='lines',
                        name='Trend',
                        line=dict(color='rgba(255, 0, 0, 0.7)', width=2, dash='dash')
                    )
                )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(family="Arial, sans-serif", size=16),
                xaxis=dict(
                    title_font=dict(family="Arial, sans-serif", size=14),
                    tickfont=dict(family="Arial, sans-serif", size=12),
                    gridcolor="rgba(220,220,220,0.4)",
                ),
                yaxis=dict(
                    title_font=dict(family="Arial, sans-serif", size=14),
                    tickfont=dict(family="Arial, sans-serif", size=12),
                    gridcolor="rgba(220,220,220,0.4)",
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Statistics for the selected particular
            st.subheader("Statistics")
            stats_df = pd.DataFrame({
                "Statistic": ["Count", "Mean", "Median", "Min", "Max", "Std Dev"],
                "Value": [
                    len(particular_df),
                    f"{particular_df['Rs'].mean():,.2f}",
                    f"{particular_df['Rs'].median():,.2f}",
                    f"{particular_df['Rs'].min():,.2f}",
                    f"{particular_df['Rs'].max():,.2f}",
                    f"{particular_df['Rs'].std():,.2f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True)
            
            # Add a gauge chart for the latest value compared to average
            latest_month = particular_df.sort_values('Month_Num', ascending=False)['Month'].iloc[0]
            latest_value = particular_df[particular_df['Month'] == latest_month]['Rs'].iloc[0]
            avg_value = particular_df['Rs'].mean()
            max_value = particular_df['Rs'].max()
            
            # Calculate percentage of latest value compared to average
            pct_of_avg = (latest_value / avg_value) * 100
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=latest_value,
                title={"text": f"Latest Value ({latest_month})"},
                delta={"reference": avg_value, "relative": True, "valueformat": ".1%"},
                gauge={
                    "axis": {"range": [0, max_value * 1.2]},
                    "bar": {"color": "#1E3A8A"},
                    "steps": [
                        {"range": [0, avg_value], "color": "lightgray"},
                        {"range": [avg_value, max_value], "color": "rgba(30, 58, 138, 0.3)"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": max_value
                    }
                }
            ))
            
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(family="Arial, sans-serif", size=12),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Month-to-month comparison
        st.subheader("Month-to-Month Comparison")
        
        # Sort by Month_Num to ensure chronological order
        month_comparison = particular_df.sort_values('Month_Num')[['Month', 'Rs']].reset_index(drop=True)
        month_comparison['Previous Month'] = month_comparison['Rs'].shift(1)
        month_comparison['Change'] = month_comparison['Rs'] - month_comparison['Previous Month']
        month_comparison['% Change'] = month_comparison['Change'] / month_comparison['Previous Month'] * 100
        
        # Create a visualization for month-to-month changes
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=month_comparison['Month'],
            y=month_comparison['Change'],
            name='Change',
            marker_color=month_comparison['Change'].apply(
                lambda x: '#10B981' if x > 0 else '#EF4444' if x < 0 else '#9CA3AF'
            )
        ))
        
        fig.update_layout(
            title="Month-to-Month Change",
            xaxis_title="Month",
            yaxis_title="Change in Amount (Rs)",
            height=400,
            template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial, sans-serif", size=12),
            title_font=dict(family="Arial, sans-serif", size=16),
            xaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
                tickangle=-45
            ),
            yaxis=dict(
                title_font=dict(family="Arial, sans-serif", size=14),
                tickfont=dict(family="Arial, sans-serif", size=12),
                gridcolor="rgba(220,220,220,0.4)",
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Format the columns for the table display
        display_month_comparison = month_comparison.copy()
        display_month_comparison['Rs'] = display_month_comparison['Rs'].apply(lambda x: f"{x:,.2f}" if not pd.isna(x) else "N/A")
        display_month_comparison['Previous Month'] = display_month_comparison['Previous Month'].apply(lambda x: f"{x:,.2f}" if not pd.isna(x) else "N/A")
        display_month_comparison['Change'] = display_month_comparison['Change'].apply(lambda x: f"{x:,.2f}" if not pd.isna(x) else "N/A")
        display_month_comparison['% Change'] = display_month_comparison['% Change'].apply(lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A")
        
        st.dataframe(display_month_comparison, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>Nepal Banking Data Analysis Dashboard | Created with Streamlit</p>", unsafe_allow_html=True)
