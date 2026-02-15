import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass
from datetime import datetime

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------

@dataclass
class Config:
    COLORS = {
        "chart_palette": [
            "#1E3A8A",
            "#2563EB",
            "#0F172A",
            "#475569",
            "#64748B"
        ]
    }
    TARGET_GNPA = 0.03
    MIN_TOTAL_CAPITAL = 0.12
    MIN_CORE_CAPITAL = 0.09


# -----------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------

def format_currency(value: float) -> str:
    return f"₹{value:,.0f}"

def generate_sample_data():
    months = pd.date_range("2023-01-01", periods=18, freq="M")

    # Trend Data
    parts = ["Loan Book", "Deposits", "Net Profit"]
    trend_records = []
    for p in parts:
        base = np.random.randint(5000, 10000)
        growth = np.random.uniform(0.01, 0.04)
        values = [base * ((1 + growth) ** i) for i in range(len(months))]
        for m, v in zip(months, values):
            trend_records.append({"Month": m, "Particulars": p, "Rs": v})

    trend_df = pd.DataFrame(trend_records)

    # NPA Data
    df_npa = pd.DataFrame({
        "Month": months,
        "Gross Npa To Gross Advances": np.linspace(0.045, 0.032, len(months)),
        "Net Npa To Net Advances": np.linspace(0.022, 0.015, len(months))
    })

    # Capital Data
    df_cap = pd.DataFrame({
        "Month": months,
        "Core Capital%": np.linspace(0.115, 0.125, len(months)),
        "Total Capital%": np.linspace(0.145, 0.16, len(months))
    })

    return trend_df, df_npa, df_cap


# -----------------------------------------------------------
# Enterprise Chart Theme
# -----------------------------------------------------------

def apply_corporate_theme(fig: go.Figure, height: int, title: str, subtitle: str = ""):
    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(size=18, color="#0F172A")
        ),
        font=dict(size=12, color="#0F172A"),
        hovermode="x unified",
        margin=dict(t=90, b=60, l=70, r=40),
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    if subtitle:
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=1.12,
            showarrow=False,
            text=subtitle,
            font=dict(size=11, color="#64748B")
        )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")

    return fig


# -----------------------------------------------------------
# Streamlit App
# -----------------------------------------------------------

st.set_page_config(page_title="Basel Analytics Dashboard", layout="wide")
st.title("Basel Analytics | Supervisory Dashboard")

trend_df, df_npa, df_cap = generate_sample_data()

tabs = st.tabs(["Performance Trend", "Asset Quality", "Capital Adequacy"])

# -----------------------------------------------------------
# Tab 1: Performance Trend
# -----------------------------------------------------------

with tabs[0]:

    chart_height = 500
    selected_parts = st.multiselect(
        "Select Portfolio Metrics",
        options=trend_df["Particulars"].unique(),
        default=trend_df["Particulars"].unique()
    )

    fig_trend = go.Figure()
    colors = Config.COLORS["chart_palette"]

    for idx, particular in enumerate(selected_parts):
        data = trend_df[trend_df["Particulars"] == particular].sort_values("Month")

        fig_trend.add_trace(
            go.Scatter(
                x=data["Month"],
                y=data["Rs"],
                name=particular,
                mode="lines+markers",
                line=dict(width=3, color=colors[idx % len(colors)]),
                marker=dict(size=8)
            )
        )

        latest_x = data["Month"].iloc[-1]
        latest_y = data["Rs"].iloc[-1]

        fig_trend.add_annotation(
            x=latest_x,
            y=latest_y,
            text=f"<b>{format_currency(latest_y)}</b>",
            showarrow=True,
            arrowhead=2
        )

        if len(data) > 2:
            cagr = (data["Rs"].iloc[-1] / data["Rs"].iloc[0]) ** (1/len(data)) - 1
            volatility = data["Rs"].pct_change().std()

            fig_trend.add_annotation(
                xref="paper",
                yref="paper",
                x=0.99,
                y=0.01 - (idx * 0.06),
                text=f"{particular} | CAGR: {cagr:.2%} | Vol: {volatility:.2%}",
                showarrow=False,
                align="right"
            )

    fig_trend.update_yaxes(tickprefix="₹", separatethousands=True)

    fig_trend = apply_corporate_theme(
        fig_trend,
        chart_height,
        title="Portfolio Performance Trend",
        subtitle="Monthly Values | INR"
    )

    st.plotly_chart(fig_trend, use_container_width=True)


# -----------------------------------------------------------
# Tab 2: Asset Quality
# -----------------------------------------------------------

with tabs[1]:

    fig_npa = go.Figure()

    max_y = df_npa["Gross Npa To Gross Advances"].max() * 1.2

    fig_npa.add_hrect(y0=0, y1=Config.TARGET_GNPA, fillcolor="#DCFCE7", opacity=0.3, line_width=0)
    fig_npa.add_hrect(y0=Config.TARGET_GNPA, y1=Config.TARGET_GNPA * 1.5, fillcolor="#FEF3C7", opacity=0.3, line_width=0)
    fig_npa.add_hrect(y0=Config.TARGET_GNPA * 1.5, y1=max_y, fillcolor="#FEE2E2", opacity=0.3, line_width=0)

    fig_npa.add_trace(
        go.Bar(
            x=df_npa["Month"],
            y=df_npa["Gross Npa To Gross Advances"],
            name="Gross NPA"
        )
    )

    fig_npa.add_trace(
        go.Scatter(
            x=df_npa["Month"],
            y=df_npa["Net Npa To Net Advances"],
            name="Net NPA",
            mode="lines+markers"
        )
    )

    fig_npa.update_yaxes(tickformat=".2%")

    fig_npa = apply_corporate_theme(
        fig_npa,
        500,
        title="Asset Quality Trend",
        subtitle="Gross vs Net NPA | Regulatory Risk Bands"
    )

    st.plotly_chart(fig_npa, use_container_width=True)


# -----------------------------------------------------------
# Tab 3: Capital Adequacy
# -----------------------------------------------------------

with tabs[2]:

    fig_cap = go.Figure()

    fig_cap.add_trace(
        go.Scatter(
            x=df_cap["Month"],
            y=df_cap["Core Capital%"],
            name="Tier 1 Capital",
            fill="tozeroy",
            line=dict(width=3)
        )
    )

    fig_cap.add_trace(
        go.Scatter(
            x=df_cap["Month"],
            y=df_cap["Total Capital%"],
            name="Total Capital (CAR)",
            fill="tozeroy",
            line=dict(width=3)
        )
    )

    fig_cap.add_hline(y=Config.MIN_TOTAL_CAPITAL, line_dash="dash")
    fig_cap.add_hline(y=Config.MIN_CORE_CAPITAL, line_dash="dot")

    fig_cap.update_yaxes(tickformat=".1%")

    fig_cap = apply_corporate_theme(
        fig_cap,
        500,
        title="Capital Adequacy Position",
        subtitle="Tier 1 and Total CAR | Regulatory Thresholds"
    )

    st.plotly_chart(fig_cap, use_container_width=True)
