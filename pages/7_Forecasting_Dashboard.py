import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import cast
from prophet import Prophet
from sqlalchemy import create_engine

from config import DATABASE_URL

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="AI Forecasting Center",
    page_icon="📉",
    layout="wide"
)

with open("dashboard_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

# ======================================================
# LOAD SALES DATA
# ======================================================

@st.cache_data(ttl=15)
def load_sales():

    orders = pd.read_sql("SELECT * FROM orders", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    daily_sales = (
        orders.groupby(orders["order_date"].dt.date)["net_amount"]
        .sum()
        .reset_index()
    )

    daily_sales.columns = ["ds", "y"]
    daily_sales["ds"] = pd.to_datetime(daily_sales["ds"])

    return orders, daily_sales


orders, daily_sales = load_sales()

# ======================================================
# HERO SECTION
# ======================================================
st.html("""
<div class="hero-small">
    <div class="hero-chip">COMMERCEIQ AI FORECASTING ENGINE</div>

    <h1>AI Forecasting & Predictive Analytics Center</h1>

    <p>
        Predict future revenue, identify sales trends, detect anomalies and
        support strategic planning with AI-powered predictive business analytics.
    </p>
</div>
""")

# ======================================================
# REFRESH DASHBOARD BUTTON
# ======================================================

col1, col2 = st.columns([8, 2])

with col2:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()   # Clear cached queries
        st.cache_resource.clear()
        st.rerun()              # Reload page
        
# ======================================================
# FORECAST CONTROLS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Forecast Configuration</h2>
    <p>Configure prediction horizon and seasonality before generating AI revenue forecasts.</p>
</div>
""", unsafe_allow_html=True)

control1, control2 = st.columns([2,1])

with control1:
    days = st.slider(
        "Forecast Horizon (Days)",
        min_value=7,
        max_value=90,
        value=30
    )

with control2:
    seasonality = st.toggle(
        "Weekly Seasonality",
        value=True
    )

st.divider()

# ======================================================
# KPI CALCULATIONS
# ======================================================

total_revenue = daily_sales["y"].sum()

avg_daily_sales = daily_sales["y"].mean()

growth_rate = daily_sales["y"].pct_change().fillna(0).mean() * 100

historical_days = len(daily_sales)

best_day = daily_sales.loc[daily_sales["y"].idxmax()]

worst_day = daily_sales.loc[daily_sales["y"].idxmin()]

# ======================================================
# AI BUSINESS SNAPSHOT
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Predictive Business Snapshot</h2>
    <p>Historical sales performance summary before AI forecasting.</p>
</div>
""", unsafe_allow_html=True)

row1 = st.columns(4)

with row1[0]:
    st.metric("💰 Historical Revenue", f"₹{total_revenue:,.0f}")

with row1[1]:
    st.metric("📆 Avg Daily Revenue", f"₹{avg_daily_sales:,.0f}")

with row1[2]:
    st.metric("📈 Avg Growth Rate", f"{growth_rate:.2f}%")

with row1[3]:
    st.metric("🗓️ Historical Days", historical_days)

st.divider()

# ======================================================
# HISTORICAL PERFORMANCE SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📊 Historical Revenue Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Highest Revenue Day",
            f"₹{best_day['y']:,.0f}"
        )

    with c2:
        st.metric(
            "Lowest Revenue Day",
            f"₹{worst_day['y']:,.0f}"
        )

    st.info(
        "CommerceIQ AI analyzes historical sales behaviour to build forecasting models, detect growth patterns and estimate future business performance."
    )

st.divider()

# ======================================================
# HISTORICAL REVENUE TREND
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Historical Revenue Trend</h2>
    <p>Analyze daily revenue performance and identify historical business growth patterns.</p>
</div>
""", unsafe_allow_html=True)

fig_history = px.area(
    daily_sales,
    x="ds",
    y="y",
    template="plotly_dark"
)

fig_history.update_traces(
    line=dict(color="#38BDF8", width=3),
    fillcolor="rgba(56,189,248,0.25)"
)

fig_history.update_layout(
    title="Daily Revenue History",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_history, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# REVENUE SMOOTHING (7-DAY ROLLING AVERAGE)
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Revenue Smoothing Analysis</h2>
    <p>Compare actual revenue with a 7-day rolling average to identify long-term business trends.</p>
</div>
""", unsafe_allow_html=True)

rolling = daily_sales.copy()
rolling["Rolling Revenue"] = rolling["y"].rolling(7).mean()

fig_rolling = go.Figure()

fig_rolling.add_trace(
    go.Scatter(
        x=rolling["ds"],
        y=rolling["y"],
        mode="lines",
        name="Daily Revenue",
        line=dict(color="#38BDF8", width=2)
    )
)

fig_rolling.add_trace(
    go.Scatter(
        x=rolling["ds"],
        y=rolling["Rolling Revenue"],
        mode="lines",
        name="7-Day Rolling Average",
        line=dict(color="#10B981", width=3)
    )
)

fig_rolling.update_layout(
    template="plotly_dark",
    title="Actual Revenue vs Rolling Average",
    height=450,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    legend=dict(
        orientation="h",
        y=-0.15
    ),
    margin=dict(l=10, r=10, t=60, b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_rolling, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# TREND INSIGHTS
# ======================================================

rolling_growth = (
    rolling["Rolling Revenue"]
    .pct_change()
    .fillna(0)
    .mean() * 100
)

with st.container(border=True):

    st.subheader("📈 Trend Insights")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Rolling Growth Rate",
            f"{rolling_growth:.2f}%"
        )

    with c2:
        st.metric(
            "Historical Average Revenue",
            f"₹{rolling['y'].mean():,.0f}"
        )

    st.info(
        "The rolling average smooths short-term fluctuations and helps CommerceIQ AI identify long-term revenue direction before generating future forecasts."
    )

st.divider()

# ======================================================
# AI REVENUE FORECAST (PROPHET MODEL)
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Revenue Forecast</h2>
    <p>Predict future business revenue using Prophet Machine Learning with confidence intervals and AI-driven forecasting.</p>
</div>
""", unsafe_allow_html=True)

if len(daily_sales) >= 10:

    # ---------------- Prophet Model ----------------

    model = Prophet(
        weekly_seasonality=cast(str, seasonality),
        daily_seasonality=cast(str, False),
        yearly_seasonality=cast(str, False)
    )

    model.fit(daily_sales)

    future = model.make_future_dataframe(periods=days)

    forecast = model.predict(future)

    prediction = forecast[["ds", "yhat"]].tail(days)

    expected_revenue = prediction["yhat"].sum()
    max_prediction = prediction["yhat"].max()
    min_prediction = prediction["yhat"].min()
    avg_prediction = prediction["yhat"].mean()

    # ======================================================
    # FORECAST KPI SNAPSHOT
    # ======================================================

    row = st.columns(4)

    with row[0]:
        st.metric("💰 Expected Revenue", f"₹{expected_revenue:,.0f}")

    with row[1]:
        st.metric("📈 Avg Forecast / Day", f"₹{avg_prediction:,.0f}")

    with row[2]:
        st.metric("🚀 Peak Forecast Day", f"₹{max_prediction:,.0f}")

    with row[3]:
        st.metric("📉 Lowest Forecast Day", f"₹{min_prediction:,.0f}")

    st.divider()

    # ======================================================
    # FORECAST CHART
    # ======================================================

    fig_forecast = go.Figure()

    # Historical Revenue
    fig_forecast.add_trace(
        go.Scatter(
            x=daily_sales["ds"],
            y=daily_sales["y"],
            mode="lines",
            name="Historical Revenue",
            line=dict(color="#38BDF8", width=2)
        )
    )

    # Forecast
    fig_forecast.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat"],
            mode="lines",
            name="AI Forecast",
            line=dict(color="#10B981", width=3)
        )
    )

    # Upper Confidence
    fig_forecast.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        )
    )

    # Lower Confidence Area
    fig_forecast.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            fill="tonexty",
            mode="lines",
            name="Confidence Interval",
            line=dict(width=0),
            fillcolor="rgba(16,185,129,0.18)"
        )
    )

    fig_forecast.update_layout(
        title="Historical Revenue vs AI Revenue Forecast",
        template="plotly_dark",
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,.95)",
        font=dict(color="#F8FAFC"),
        legend=dict(
            orientation="h",
            y=-0.18
        ),
        margin=dict(l=10, r=10, t=60, b=30)
    )

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_forecast, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ======================================================
    # FORECAST EXECUTIVE SUMMARY
    # ======================================================

    highest_date_raw = str(prediction.at[prediction["yhat"].idxmax(), "ds"])
    lowest_date_raw = str(prediction.at[prediction["yhat"].idxmin(), "ds"])

    highest_date = pd.to_datetime(highest_date_raw)
    lowest_date = pd.to_datetime(lowest_date_raw)

    with st.container(border=True):

        st.subheader("🤖 Forecast Executive Summary")

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Highest Revenue Forecast Date",
                highest_date.strftime("%d %b %Y")
            )

            st.metric(
                "Peak Forecast Revenue",
                f"₹{max_prediction:,.0f}"
            )

        with c2:
            st.metric(
                "Lowest Revenue Forecast Date",
                lowest_date.strftime("%d %b %Y")
            )

            st.metric(
                "Minimum Forecast Revenue",
                f"₹{min_prediction:,.0f}"
            )

        st.success(
            f"CommerceIQ AI predicts approximately ₹{expected_revenue:,.0f} revenue over the next {days} days based on historical business trends and seasonality patterns."
        )

    st.divider()

else:

    st.warning(
        "At least 10 days of historical sales data are required before generating an AI revenue forecast."
    )

    st.stop()

# ======================================================
# FORECAST TREND COMPONENTS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Forecast Trend Components</h2>
    <p>Understand the long-term revenue trend learned by the AI forecasting model.</p>
</div>
""", unsafe_allow_html=True)

trend = forecast[["ds", "trend"]]

fig_trend = px.line(
    trend,
    x="ds",
    y="trend",
    template="plotly_dark"
)

fig_trend.update_traces(
    line=dict(color="#22D3EE", width=3)
)

fig_trend.update_layout(
    title="Underlying Revenue Trend",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# WEEKDAY REVENUE ANALYSIS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Revenue by Weekday</h2>
    <p>Identify which weekdays consistently generate the highest average revenue.</p>
</div>
""", unsafe_allow_html=True)

weekday = daily_sales.copy()

weekday["Weekday"] = weekday["ds"].dt.day_name()

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday["Weekday"] = pd.Categorical(
    weekday["Weekday"],
    categories=weekday_order,
    ordered=True
)

weekday_summary = (
    weekday.groupby("Weekday")["y"]
    .mean()
    .reset_index()
)

left, right = st.columns([1.3, 0.7])

# ------------------------------------------------------
# Weekday Revenue Chart
# ------------------------------------------------------

fig_weekday = px.bar(
    weekday_summary,
    x="Weekday",
    y="y",
    color="y",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_weekday.update_layout(
    title="Average Revenue by Weekday",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    coloraxis_showscale=False,
    margin=dict(l=10, r=10, t=60, b=20)
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_weekday, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# Weekday Executive Summary
# ------------------------------------------------------

top_weekday = weekday_summary.sort_values("y", ascending=False).iloc[0]
low_weekday = weekday_summary.sort_values("y").iloc[0]

with right:
    with st.container(border=True):

        st.subheader("📅 Weekday Insights")

        st.metric(
            "Highest Revenue Day",
            top_weekday["Weekday"]
        )

        st.metric(
            "Average Revenue",
            f"₹{top_weekday['y']:,.0f}"
        )

        st.metric(
            "Lowest Revenue Day",
            low_weekday["Weekday"]
        )

        st.metric(
            "Average Revenue",
            f"₹{low_weekday['y']:,.0f}"
        )

st.divider()

# ======================================================
# FORECAST COMPONENT SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📊 Forecast Component Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Historical Average Revenue",
            f"₹{daily_sales['y'].mean():,.0f}"
        )

    with c2:
        st.metric(
            "Predicted Daily Average",
            f"₹{prediction['yhat'].mean():,.0f}"
        )

    st.info(
        "CommerceIQ AI analyzes historical seasonality and weekday demand patterns to estimate future business revenue more accurately."
    )

st.divider()

# ======================================================
# REVENUE ANOMALY DETECTION
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Revenue Anomaly Detection</h2>
    <p>CommerceIQ AI automatically detects unusual revenue spikes and drops using statistical anomaly detection.</p>
</div>
""", unsafe_allow_html=True)

anomaly = daily_sales.copy()

mean_revenue = anomaly["y"].mean()
std_revenue = anomaly["y"].std()

anomaly["Anomaly"] = anomaly["y"].apply(
    lambda value: "Anomaly"
    if abs(value - mean_revenue) > (2 * std_revenue)
    else "Normal"
)

left, right = st.columns([1.4, 0.6])

# ------------------------------------------------------
# Anomaly Chart
# ------------------------------------------------------

fig_anomaly = px.scatter(
    anomaly,
    x="ds",
    y="y",
    color="Anomaly",
    color_discrete_map={
        "Normal": "#38BDF8",
        "Anomaly": "#EF4444"
    },
    template="plotly_dark"
)

fig_anomaly.update_layout(
    title="Revenue Anomaly Detection Timeline",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    legend=dict(orientation="h", y=-0.15),
    margin=dict(l=10, r=10, t=60, b=20)
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_anomaly, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# Anomaly Summary
# ------------------------------------------------------

anomaly_count = (anomaly["Anomaly"] == "Anomaly").sum()
normal_count = (anomaly["Anomaly"] == "Normal").sum()

highest_anomaly = anomaly.sort_values("y", ascending=False).iloc[0]

with right:
    with st.container(border=True):

        st.subheader("🚨 AI Detection Summary")

        st.metric("Anomaly Days", anomaly_count)

        st.metric("Normal Days", normal_count)

        st.metric(
            "Largest Revenue Spike",
            f"₹{highest_anomaly['y']:,.0f}"
        )

st.divider()

# ======================================================
# PREDICTED REVENUE TABLE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Predicted Revenue Table</h2>
    <p>Daily AI revenue predictions generated for the selected forecast horizon.</p>
</div>
""", unsafe_allow_html=True)

forecast_table = prediction.copy()

forecast_table.columns = [
    "Forecast Date",
    "Predicted Revenue"
]

forecast_table["Predicted Revenue"] = (
    forecast_table["Predicted Revenue"].round(0)
)

with st.container(border=True):

    st.subheader("📅 AI Revenue Forecast Schedule")

    st.dataframe(
        forecast_table,
        use_container_width=True,
        height=420
    )

st.divider()

# ======================================================
# FORECAST TABLE SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📋 Forecast Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Forecast Days",
            len(forecast_table)
        )

    with c2:
        st.metric(
            "Average Daily Forecast",
            f"₹{forecast_table['Predicted Revenue'].mean():,.0f}"
        )

    with c3:
        st.metric(
            "Expected Forecast Revenue",
            f"₹{forecast_table['Predicted Revenue'].sum():,.0f}"
        )

    st.success(
        "The prediction table is generated directly from the CommerceIQ AI forecasting model and is ready for Excel export and executive reporting."
    )

st.divider()

# ======================================================
# AI BUSINESS OUTLOOK
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Business Outlook</h2>
    <p>CommerceIQ AI summarizes the forecast into executive-level business recommendations.</p>
</div>
""", unsafe_allow_html=True)

outlook = "Growth 📈" if growth_rate >= 0 else "Decline 📉"

with st.container(border=True):

    st.subheader("🤖 Executive Forecast Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Business Outlook", outlook)
        st.metric("Forecast Horizon", f"{days} Days")
        st.metric("Expected Revenue", f"₹{expected_revenue:,.0f}")

    with c2:
        st.metric("Average Daily Forecast", f"₹{avg_prediction:,.0f}")
        st.metric("Highest Forecast", f"₹{max_prediction:,.0f}")
        st.metric("Lowest Forecast", f"₹{min_prediction:,.0f}")

    st.success(
        f"CommerceIQ AI predicts approximately ₹{expected_revenue:,.0f} revenue during the next {days} days based on historical sales trends and seasonality."
    )

st.divider()

# ======================================================
# AI STRATEGIC RECOMMENDATIONS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Strategic Recommendations</h2>
    <p>Machine Learning insights for inventory, marketing and revenue optimization.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):
        st.markdown("### 📦 Inventory Planning")
        st.write(
            "- Increase stock before forecasted demand peaks.\n"
            "- Monitor products during high forecast periods.\n"
            "- Prepare warehouse inventory for projected sales volume."
        )

    with st.container(border=True):
        st.markdown("### 📈 Revenue Growth")
        st.write(
            "- Allocate marketing budget before predicted peak days.\n"
            "- Launch promotional campaigns during strong forecast windows.\n"
            "- Track revenue anomalies for unexpected opportunities."
        )

with col2:

    with st.container(border=True):
        st.markdown("### 👥 Customer Strategy")
        st.write(
            "- Focus retention campaigns on repeat purchase periods.\n"
            "- Target high-performing weekdays for customer engagement.\n"
            "- Monitor regional demand during forecast growth."
        )

    with st.container(border=True):
        st.markdown("### 🤖 CommerceIQ AI Insight")
        st.write(
            "- Historical trends drive future revenue predictions.\n"
            "- Weekly seasonality improves forecasting accuracy.\n"
            "- Confidence intervals help estimate business uncertainty."
        )

st.divider()

# ======================================================
# DOWNLOAD FORECAST REPORT
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Export AI Forecast Report</h2>
    <p>Download the AI-generated revenue forecast as an executive-ready CSV report.</p>
</div>
""", unsafe_allow_html=True)

forecast_csv = forecast_table.to_csv(index=False)

with st.container(border=True):

    st.subheader("📄 Forecast Report Export")

    st.write(
        "The exported report contains forecast dates and predicted revenue generated by CommerceIQ AI."
    )

    st.download_button(
        label="📥 Download AI Revenue Forecast",
        data=forecast_csv,
        file_name="CommerceIQ_AI_Revenue_Forecast.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

# ======================================================
# FORECAST ENGINE STATUS
# ======================================================

with st.container(border=True):

    st.subheader("⚙️ Forecast Engine Status")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("AI Model", "Prophet ML")

    with c2:
        st.metric("Forecast Horizon", f"{days} Days")

    with c3:
        st.metric("Seasonality", "Enabled" if seasonality else "Disabled")

    st.info(
        "Forecast generated using CommerceIQ AI Predictive Analytics Engine with historical sales trend modelling."
    )

st.divider()

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-premium">

## CommerceIQ AI Predictive Intelligence

Revenue Forecasting • Trend Analysis • Anomaly Detection • Strategic Business Planning

<div class="footer-links">
    <span>AI Forecasting</span>
    <span>Revenue Intelligence</span>
    <span>Anomaly Detection</span>
    <span>Executive Planning</span>
</div>

<hr>

<p class="copyright">
© 2026 CommerceIQ • AI Forecasting & Predictive Analytics Center
</p>

</div>
""", unsafe_allow_html=True)