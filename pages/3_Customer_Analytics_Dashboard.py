import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

from config import DATABASE_URL

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Customer Intelligence Dashboard",
    page_icon="👥",
    layout="wide"
)

# Load CommerceIQ Global Theme
with open("dashboard_style.css") as css:
    st.markdown(
        f"<style>{css.read()}</style>",
        unsafe_allow_html=True
    )

engine = create_engine(DATABASE_URL)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=30)
def load_data():

    orders = pd.read_sql("SELECT * FROM orders", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    customer_sales = orders.merge(
        customers,
        on="customer_id",
        how="left"
    )

    return customer_sales, customers


customer_sales, customers = load_data()

# Working copy for filters
filtered = customer_sales.copy()

# ======================================================
# HERO SECTION (Premium Customer Intelligence)
# ======================================================

st.html("""
<div class="hero-small">
    <div class="hero-chip">COMMERCEIQ CUSTOMER INTELLIGENCE</div>

    <h1>Customer Analytics Dashboard</h1>

    <p>
        Analyze customer acquisition, retention, lifetime value, purchasing behaviour,
        geographic distribution and loyalty insights through enterprise-grade analytics.
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
# SIDEBAR FILTERS
# ======================================================

st.sidebar.markdown("## Customer Filters")

city_filter = st.sidebar.multiselect(
    "Select City",
    sorted(customer_sales["city"].dropna().unique()),
    default=sorted(customer_sales["city"].dropna().unique())
)

country_filter = st.sidebar.multiselect(
    "Select Country",
    sorted(customer_sales["country"].dropna().unique()),
    default=sorted(customer_sales["country"].dropna().unique())
)

date_range = st.sidebar.date_input(
    "Order Date Range",
    (
        customer_sales["order_date"].min().date(),
        customer_sales["order_date"].max().date()
    )
)

filtered = customer_sales[
    customer_sales["city"].isin(city_filter) &
    customer_sales["country"].isin(country_filter)
]

if len(date_range) == 2:
    filtered = filtered[
        (filtered["order_date"].dt.date >= date_range[0]) &
        (filtered["order_date"].dt.date <= date_range[1])
    ]

# ======================================================
# KPI CALCULATIONS
# ======================================================

total_customers = len(customers)

active_customers = filtered["customer_id"].nunique()

repeat_customers = (
    filtered.groupby("customer_id")
    .size()
    .gt(1)
    .sum()
)

repeat_rate = (
    repeat_customers / active_customers * 100
    if active_customers else 0
)

customer_revenue = filtered["net_amount"].sum()

avg_customer_value = (
    filtered.groupby("customer_id")["net_amount"]
    .sum()
    .mean()
)

avg_orders = (
    filtered.groupby("customer_id")
    .size()
    .mean()
)

cities_count = filtered["city"].nunique()
countries_count = filtered["country"].nunique()

# VIP Customers (> ₹10,000 Revenue)
vip_customers = (
    filtered.groupby("customer_id")["net_amount"]
    .sum()
    .gt(10000)
    .sum()
)

# ======================================================
# EXECUTIVE CUSTOMER KPIs
# ======================================================

st.html("""
<div class="section-header">
    <h2>Executive Customer KPIs</h2>
    <p>Live customer acquisition, loyalty and lifetime value metrics.</p>
</div>
""")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Customers", f"{total_customers:,}")

kpi2.metric("Active Customers", f"{active_customers:,}")

kpi3.metric("Repeat Customers", f"{repeat_customers:,}")

kpi4.metric("VIP Customers", f"{vip_customers:,}")

kpi5, kpi6, kpi7, kpi8 = st.columns(4)

kpi5.metric(
    "Customer Revenue",
    f"₹{customer_revenue:,.0f}"
)

kpi6.metric(
    "Lifetime Value",
    f"₹{avg_customer_value:,.0f}"
)

kpi7.metric(
    "Repeat Rate",
    f"{repeat_rate:.1f}%"
)

kpi8.metric(
    "Avg Orders / Customer",
    f"{avg_orders:.1f}"
)

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER SNAPSHOT CARD
# ======================================================

top_city = (
    filtered.groupby("city")["net_amount"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
    if not filtered.empty else "-"
)

top_country = (
    filtered.groupby("country")["net_amount"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
    if not filtered.empty else "-"
)

# ======================================================
# CUSTOMER INTELLIGENCE SNAPSHOT
# ======================================================

with st.container(border=True):

    st.subheader("Customer Intelligence Snapshot")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Top Customer City", top_city)
        st.metric("Cities Served", cities_count)

    with col2:
        st.metric("Top Country", top_country)
        st.metric("Countries Served", countries_count)

    st.metric(
        "Average Customer Revenue",
        f"₹{avg_customer_value:,.0f}"
    )

    st.info(
        "CommerceIQ AI continuously tracks customer loyalty, purchase frequency, customer lifetime value, and regional demand across all active customers."
    )


# ======================================================
# CUSTOMER GROWTH & RETENTION CENTER
# ======================================================

st.html("""
<div class="section-header">
    <h2>Customer Growth & Retention Center</h2>
    <p>Track active customers, acquisition trends, repeat behaviour and loyalty performance over time.</p>
</div>
""")

# ======================================================
# DAILY ACTIVE CUSTOMERS
# ======================================================

daily_active = (
    filtered.groupby(filtered["order_date"].dt.date)["customer_id"]
    .nunique()
    .reset_index(name="Active Customers")
)

fig_active = px.area(
    daily_active,
    x="order_date",
    y="Active Customers",
    color_discrete_sequence=["#38BDF8"],
    template="plotly_dark"
)

fig_active.update_layout(
    title="Daily Active Customers",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB"),
    margin=dict(l=20,r=20,t=60,b=20)
)

# ======================================================
# CUSTOMER RETENTION DONUT
# ======================================================

retention_df = pd.DataFrame({
    "Customer Type": ["Repeat Customers", "One-Time Customers"],
    "Count": [repeat_customers, active_customers - repeat_customers]
})

fig_retention = px.pie(
    retention_df,
    names="Customer Type",
    values="Count",
    hole=0.65,
    color="Customer Type",
    color_discrete_map={
        "Repeat Customers":"#22C55E",
        "One-Time Customers":"#64748B"
    },
    template="plotly_dark"
)

fig_retention.update_traces(textinfo="percent+label")

fig_retention.update_layout(
    title="Customer Retention Distribution",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E5E7EB")
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_active, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_retention, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# MONTHLY CUSTOMER ACQUISITION
# ======================================================

st.html("""
<div class="section-header">
    <h2>Customer Acquisition Trend</h2>
    <p>Monitor monthly new customer acquisition and customer activity growth.</p>
</div>
""")

filtered["Month"] = filtered["order_date"].dt.to_period("M").astype(str)

monthly_customers = (
    filtered.groupby("Month")["customer_id"]
    .nunique()
    .reset_index(name="Customers")
)

fig_monthly = px.line(
    monthly_customers,
    x="Month",
    y="Customers",
    markers=True,
    color_discrete_sequence=["#2563EB"],
    template="plotly_dark"
)

fig_monthly.update_layout(
    title="Monthly Active Customers",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB"),
    margin=dict(l=20,r=20,t=60,b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_monthly, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER LOYALTY SCORE
# ======================================================

st.html("""
<div class="section-header">
    <h2>Customer Loyalty Insights</h2>
    <p>Identify loyal customers through purchase frequency and revenue contribution.</p>
</div>
""")

customer_frequency = (
    filtered.groupby("customer_id")
    .agg(
        Orders=("order_id","count"),
        Revenue=("net_amount","sum")
    )
    .reset_index()
)

customer_frequency["Loyalty Score"] = (
    customer_frequency["Orders"] * 20
).clip(upper=100)

fig_loyalty = px.scatter(
    customer_frequency,
    x="Orders",
    y="Revenue",
    size="Revenue",
    color="Loyalty Score",
    color_continuous_scale="Blues",
    template="plotly_dark",
    hover_data=["customer_id"]
)

fig_loyalty.update_layout(
    title="Customer Loyalty Matrix",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB"),
    margin=dict(l=20,r=20,t=60,b=20)
)

# Loyalty Distribution
loyalty_bins = pd.cut(
    customer_frequency["Loyalty Score"],
    bins=[0,40,70,100],
    labels=["Low","Medium","High"]
)

loyalty_distribution = (
    loyalty_bins.value_counts()
    .reset_index()
)

loyalty_distribution.columns = ["Level","Customers"]

fig_loyalty_pie = px.pie(
    loyalty_distribution,
    names="Level",
    values="Customers",
    hole=0.55,
    color="Level",
    color_discrete_map={
        "High":"#22C55E",
        "Medium":"#2563EB",
        "Low":"#64748B"
    },
    template="plotly_dark"
)

fig_loyalty_pie.update_layout(
    title="Loyalty Score Distribution",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E5E7EB")
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_loyalty, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_loyalty_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# GEOGRAPHIC INTELLIGENCE CENTER
# ======================================================

st.html("""
<div class="section-header">
    <h2>Geographic Intelligence Center</h2>
    <p>Monitor regional customer demand, city-wise revenue, country contribution and geographic sales intelligence.</p>
</div>
""")

# ======================================================
# GEOGRAPHIC KPI CARDS
# ======================================================

top_city = (
    filtered.groupby("city")["net_amount"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

top_country = (
    filtered.groupby("country")["net_amount"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

city_revenue = (
    filtered.groupby("city")["net_amount"]
    .sum()
    .max()
)

country_revenue = (
    filtered.groupby("country")["net_amount"]
    .sum()
    .max()
)

g1, g2, g3, g4 = st.columns(4)

g1.metric("Cities Served", cities_count)
g2.metric("Countries Served", countries_count)
g3.metric("Top City", top_city)
g4.metric("Top Country", top_country)

# ======================================================
# TOP CITY & COUNTRY REVENUE
# ======================================================

city_sales = (
    filtered.groupby("city")
    .agg(
        Revenue=("net_amount","sum"),
        Customers=("customer_id","nunique"),
        Orders=("order_id","count")
    )
    .sort_values("Revenue", ascending=False)
    .head(10)
    .reset_index()
)

country_sales = (
    filtered.groupby("country")
    .agg(
        Revenue=("net_amount","sum"),
        Customers=("customer_id","nunique")
    )
    .sort_values("Revenue", ascending=False)
    .reset_index()
)

fig_city = px.bar(
    city_sales,
    x="Revenue",
    y="city",
    orientation="h",
    color="Revenue",
    color_continuous_scale=["#1E40AF","#38BDF8"],
    template="plotly_dark"
)

fig_city.update_layout(
    title="Top Revenue Generating Cities",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    font=dict(color="#E5E7EB")
)

fig_country = px.pie(
    country_sales,
    names="country",
    values="Revenue",
    hole=.60,
    color_discrete_sequence=px.colors.sequential.Blues_r,
    template="plotly_dark"
)

fig_country.update_traces(textinfo="percent+label")

fig_country.update_layout(
    title="Revenue Contribution by Country",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E5E7EB")
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_city, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_country, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER DENSITY BY CITY
# ======================================================

st.html("""
<div class="section-header">
    <h2>Customer Density Analytics</h2>
    <p>Compare customer concentration and revenue across major cities.</p>
</div>
""")

density = (
    filtered.groupby("city")
    .agg(
        Customers=("customer_id","nunique"),
        Revenue=("net_amount","sum")
    )
    .sort_values("Customers", ascending=False)
    .head(12)
    .reset_index()
)

fig_density = px.scatter(
    density,
    x="Customers",
    y="Revenue",
    size="Revenue",
    color="Customers",
    hover_name="city",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_density.update_layout(
    title="Customer Density vs Revenue",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB")
)

# Revenue Share
fig_share = px.treemap(
    city_sales,
    path=["city"],
    values="Revenue",
    color="Revenue",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_share.update_layout(
    title="Revenue Share by City",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E5E7EB")
)

c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_density, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_share, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# GEOGRAPHIC LEADERBOARD
# ======================================================

st.html("""
<div class="section-header">
    <h2>Geographic Revenue Leaderboard</h2>
    <p>Highest performing cities ranked by revenue, customers and order volume.</p>
</div>
""")

leaderboard = city_sales.copy()

leaderboard["Avg Revenue / Customer"] = (
    leaderboard["Revenue"] / leaderboard["Customers"]
).round(0)

leaderboard = leaderboard.rename(columns={
    "city":"City",
    "Revenue":"Revenue (₹)",
    "Customers":"Customers",
    "Orders":"Orders"
})

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

st.dataframe(
    leaderboard,
    use_container_width=True,
    height=380
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# REGIONAL BUSINESS SUMMARY
# ======================================================

# ======================================================
# REGIONAL BUSINESS SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("🌍 Regional Business Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Top Revenue City", top_city)
        st.metric("Revenue Generated", f"₹{city_revenue:,.0f}")
        st.metric("Cities Served", cities_count)

    with c2:
        st.metric("Top Revenue Country", top_country)
        st.metric("Country Revenue", f"₹{country_revenue:,.0f}")
        st.metric("Countries Served", countries_count)

    st.info(
        "CommerceIQ continuously identifies regional growth opportunities by analysing customer concentration, order volume, and city-level revenue trends."
    )

st.divider()

# ======================================================
# CUSTOMER SEGMENTATION & PURCHASE BEHAVIOR CENTER
# ======================================================

st.html("""
<div class="section-header">
    <h2>Customer Segmentation & Purchase Behavior</h2>
    <p>Identify VIP customers, spending patterns, purchase frequency and lifetime value distribution.</p>
</div>
""")

# ======================================================
# CUSTOMER VALUE SEGMENTS
# ======================================================

customer_value = (
    filtered.groupby("customer_id")
    .agg(
        Revenue=("net_amount","sum"),
        Orders=("order_id","count")
    )
    .reset_index()
)

customer_value["Segment"] = pd.cut(
    customer_value["Revenue"],
    bins=[0,3000,10000,100000000],
    labels=["Low Value","Medium Value","High Value"]
)

segment_df = (
    customer_value["Segment"]
    .value_counts()
    .reset_index()
)

segment_df.columns=["Segment","Customers"]

fig_segment = px.pie(
    segment_df,
    names="Segment",
    values="Customers",
    hole=.60,
    color="Segment",
    color_discrete_map={
        "High Value":"#22C55E",
        "Medium Value":"#2563EB",
        "Low Value":"#64748B"
    },
    template="plotly_dark"
)

fig_segment.update_layout(
    title="Customer Value Segments",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E5E7EB")
)

# ======================================================
# CLV DISTRIBUTION
# ======================================================

fig_clv = px.histogram(
    customer_value,
    x="Revenue",
    nbins=25,
    color_discrete_sequence=["#38BDF8"],
    template="plotly_dark"
)

fig_clv.update_layout(
    title="Customer Lifetime Value Distribution",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB")
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_segment, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_clv, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PURCHASE FREQUENCY ANALYTICS
# ======================================================

st.html("""
<div class="section-header">
    <h2>Purchase Frequency Analytics</h2>
    <p>Understand how often customers purchase and identify loyal buyers.</p>
</div>
""")

frequency_df = (
    filtered.groupby("customer_id")
    .size()
    .reset_index(name="Orders")
)

fig_frequency = px.histogram(
    frequency_df,
    x="Orders",
    nbins=20,
    color_discrete_sequence=["#2563EB"],
    template="plotly_dark"
)

fig_frequency.update_layout(
    title="Orders Per Customer",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB")
)

# ======================================================
# MONTHLY CUSTOMER REVENUE
# ======================================================

monthly_revenue = (
    filtered.groupby(filtered["order_date"].dt.to_period("M").astype(str))["net_amount"]
    .sum()
    .reset_index(name="Revenue")
)

fig_monthly = px.line(
    monthly_revenue,
    x="order_date",
    y="Revenue",
    markers=True,
    color_discrete_sequence=["#22D3EE"],
    template="plotly_dark"
)

fig_monthly.update_layout(
    title="Monthly Customer Revenue",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB")
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_frequency, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_monthly, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# TOP REVENUE CUSTOMERS
# ======================================================

st.html("""
<div class="section-header">
    <h2>Top Revenue Customers</h2>
    <p>Highest value customers ranked by total lifetime revenue.</p>
</div>
""")

top_customers = (
    filtered.groupby(
        ["customer_id","first_name","last_name","city"]
    )
    .agg(
        Revenue=("net_amount","sum"),
        Orders=("order_id","count")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
    .head(15)
)

top_customers["Customer"] = (
    top_customers["first_name"] + " " + top_customers["last_name"]
)

fig_top = px.bar(
    top_customers.sort_values("Revenue"),
    x="Revenue",
    y="Customer",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_top.update_layout(
    title="Top 15 Revenue Customers",
    height=520,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    font=dict(color="#E5E7EB")
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_top, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# VIP CUSTOMER TABLE
# ======================================================

st.html("""
<div class="section-header">
    <h2>VIP Customer Leaderboard</h2>
    <p>Enterprise customer ranking based on revenue and purchase frequency.</p>
</div>
""")

vip_table = top_customers.copy()

vip_table["Average Order"] = (
    vip_table["Revenue"] / vip_table["Orders"]
).round(0)

vip_table = vip_table.rename(columns={
    "city":"City"
})

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

st.dataframe(
    vip_table[
        [
            "customer_id",
            "Customer",
            "City",
            "Orders",
            "Revenue",
            "Average Order"
        ]
    ],
    use_container_width=True,
    height=380
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER INSIGHT SUMMARY
# ======================================================

high_value = segment_df.loc[
    segment_df["Segment"]=="High Value",
    "Customers"
].sum()

medium_value = segment_df.loc[
    segment_df["Segment"]=="Medium Value",
    "Customers"
].sum()

low_value = segment_df.loc[
    segment_df["Segment"]=="Low Value",
    "Customers"
].sum()

# ======================================================
# CUSTOMER INTELLIGENCE SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("🧠 Customer Intelligence Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("High Value Customers", high_value)
        st.metric("Medium Value Customers", medium_value)

    with c2:
        st.metric("Low Value Customers", low_value)
        st.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

    with c3:
        st.metric(
            "Average Customer Lifetime Value",
            f"₹{avg_customer_value:,.0f}"
        )

    st.info(
        "CommerceIQ AI identifies loyal customers, predicts customer value segments, and helps prioritize retention campaigns for maximum lifetime revenue."
    )

st.divider()

st.divider()

# ======================================================
# LIVE CUSTOMER INTELLIGENCE CENTER
# ======================================================

st.markdown("""
<div class='section-header'>
    <h2>Live Customer Intelligence Center</h2>
    <p>Monitor latest customer activity, VIP customers, detailed customer analytics and export enterprise reports.</p>
</div>
""", unsafe_allow_html=True)

# Latest Customer Activity
latest_activity = (
    filtered.sort_values("order_date", ascending=False)
    .head(12)
)

# VIP Customers
vip_customers = (
    filtered.groupby(
        ["customer_id", "first_name", "last_name", "city"]
    )
    .agg(
        Revenue=("net_amount", "sum"),
        Orders=("order_id", "count")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
    .head(12)
)

vip_customers["Customer"] = (
    vip_customers["first_name"] + " " + vip_customers["last_name"]
)

col1, col2 = st.columns(2)

# ------------------------------------------------------
# Latest Orders Feed
# ------------------------------------------------------

with col1:

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    st.markdown("#### Latest Customer Orders")

    st.dataframe(
        latest_activity[
            [
                "order_date",
                "customer_id",
                "first_name",
                "last_name",
                "city",
                "net_amount"
            ]
        ].rename(columns={
            "order_date": "Order Date",
            "first_name": "First Name",
            "last_name": "Last Name",
            "city": "City",
            "net_amount": "Revenue"
        }),
        use_container_width=True,
        height=380
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# VIP Customer Feed
# ------------------------------------------------------

with col2:

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    st.markdown("#### VIP Customers Leaderboard")

    st.dataframe(
        vip_customers[
            [
                "Customer",
                "city",
                "Orders",
                "Revenue"
            ]
        ].rename(columns={
            "city": "City"
        }),
        use_container_width=True,
        height=380
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER MASTER ANALYTICS TABLE
# ======================================================

st.markdown("""
<div class='section-header'>
    <h2>Customer Master Analytics</h2>
    <p>Complete customer performance table with revenue, orders and average order value.</p>
</div>
""", unsafe_allow_html=True)

customer_master = (
    filtered.groupby(
        [
            "customer_id",
            "first_name",
            "last_name",
            "city",
            "country"
        ]
    )
    .agg(
        Orders=("order_id", "count"),
        Revenue=("net_amount", "sum"),
        Average_Order=("net_amount", "mean")
    )
    .reset_index()
)

customer_master["Customer"] = (
    customer_master["first_name"] + " " + customer_master["last_name"]
)

customer_master = customer_master.rename(columns={
    "city": "City",
    "country": "Country",
    "Average_Order": "Average Order Value"
})

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

st.dataframe(
    customer_master[
        [
            "customer_id",
            "Customer",
            "City",
            "Country",
            "Orders",
            "Revenue",
            "Average Order Value"
        ]
    ].sort_values("Revenue", ascending=False),
    use_container_width=True,
    height=500
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER INSIGHT SUMMARY
# ======================================================

top_customer = customer_master.sort_values(
    "Revenue", ascending=False
).iloc[0]

# ======================================================
# CUSTOMER EXECUTIVE INSIGHTS
# ======================================================

with st.container(border=True):

    st.subheader("Customer Executive Insights")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Top Revenue Customer", top_customer["Customer"])
        st.metric("Customer Revenue", f"₹{top_customer['Revenue']:,.0f}")
        st.metric("Cities Served", cities_count)

    with c2:
        st.metric("Total Customer Revenue", f"₹{customer_revenue:,.0f}")
        st.metric("Average Lifetime Value", f"₹{avg_customer_value:,.0f}")
        st.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

    st.success(
        "CommerceIQ AI identifies high-value customers, analyzes purchase frequency, predicts customer lifetime value, and highlights loyalty opportunities for executive decision-making."
    )

st.divider()

# ======================================================
# EXPORT CUSTOMER REPORT
# ======================================================

csv = customer_master.to_csv(index=False).encode("utf-8")

st.markdown("""
### CommerceIQ Customer Analytics Export""")

st.download_button(
    label="Download Customer Analytics Report",
    data=csv,
    file_name="CommerceIQ_Customer_Analytics_Report.csv",
    mime="text/csv",
    use_container_width=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class='footer-premium'>

## CommerceIQ Executive Intelligence Platform

Enterprise Customer Intelligence • AI Powered Analytics • Business Decision Support

<div class='footer-links'>
    <span>Customer Analytics</span>
    <span>Revenue Intelligence</span>
    <span>Geographic Insights</span>
    <span>AI Executive Reports</span>
</div>

<hr>

<p class='copyright'>
© 2026 CommerceIQ • Executive Intelligence Dashboard
</p>

</div>
""", unsafe_allow_html=True)