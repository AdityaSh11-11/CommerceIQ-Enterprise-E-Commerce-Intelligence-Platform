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
    page_title="Sales Analytics Dashboard",
    page_icon="📈",
    layout="wide"
)

# Load Global CommerceIQ Theme
with open("dashboard_style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=30)
def load_data():

    orders = pd.read_sql("SELECT * FROM orders", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    sales = (
        order_items
        .merge(products, on="product_id")
        .merge(orders, on="order_id")
        .merge(customers, on="customer_id")
    )

    sales["Revenue"] = sales["quantity"] * sales["unit_price"]

    return sales

sales = load_data()

# ======================================================
# FILTERED DATA COPY
# ======================================================

filtered = sales.copy()


# ======================================================
# HERO SECTION
# ======================================================

# ======================================================
# HERO SECTION
# ======================================================

st.html("""
<div class="hero-small">
    <div class="hero-chip">COMMERCEIQ SALES INTELLIGENCE</div>

    <h1>Sales Analytics Dashboard</h1>

    <p>
        Monitor live revenue, customer demand, category performance,
        brand contribution and sales growth with enterprise-grade analytics.
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
# SIDEBAR FILTER PANEL
# ======================================================

st.sidebar.markdown("## Sales Intelligence Filters")

category = st.sidebar.multiselect(
    "Product Category",
    sorted(sales["category"].unique()),
    default=sorted(sales["category"].unique())
)

brand = st.sidebar.multiselect(
    "Brand",
    sorted(sales["brand"].unique()),
    default=sorted(sales["brand"].unique())
)

date_range = st.sidebar.date_input(
    "Order Date Range",
    (
        sales["order_date"].min().date(),
        sales["order_date"].max().date()
    )
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    date_start, date_end = date_range
else:
    date_start = date_end = date_range

# Apply Filters
filtered = sales[
    sales["category"].isin(category) &
    sales["brand"].isin(brand)
].copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = filtered[
        (filtered["order_date"].dt.date >= date_start) &
        (filtered["order_date"].dt.date <= date_end)
    ]

# ======================================================
# FILTER SUMMARY CARD
# ======================================================

st.markdown(f"""
<div class="glass-card">

### Active Sales Filters

**Categories Selected:** {len(category)}

**Brands Selected:** {len(brand)}

**Date Range:** {date_start} → {date_end}

**Filtered Transactions:** {len(filtered):,}

</div>
""", unsafe_allow_html=True)

# ======================================================
# EXECUTIVE SALES KPIs
# ======================================================

revenue = filtered["Revenue"].sum()
orders_count = filtered["order_id"].nunique()
products_sold = filtered["quantity"].sum()
aov = revenue / orders_count if orders_count else 0

categories_count = filtered["category"].nunique()
brands_count = filtered["brand"].nunique()
cities_count = filtered["city"].nunique()
avg_rating = filtered["rating"].mean()

st.markdown("""
<div class="section-header">
    <h2>Executive Sales Snapshot</h2>
    <p>Live KPIs generated from CommerceIQ filtered sales transactions.</p>
</div>
""", unsafe_allow_html=True)

kpi1 = st.columns(4)

with kpi1[0]:
    st.metric("Total Revenue", f"₹{revenue:,.0f}")

with kpi1[1]:
    st.metric("Orders Processed", f"{orders_count:,}")

with kpi1[2]:
    st.metric("Products Sold", f"{int(products_sold):,}")

with kpi1[3]:
    st.metric("Average Order Value", f"₹{aov:,.0f}")

kpi2 = st.columns(4)

with kpi2[0]:
    st.metric("Categories", categories_count)

with kpi2[1]:
    st.metric("Brands", brands_count)

with kpi2[2]:
    st.metric("Average Rating", f"{avg_rating:.1f}")

with kpi2[3]:
    st.metric("Customer Cities", cities_count)


# ======================================================
# SALES PERFORMANCE ANALYTICS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Sales Performance Analytics</h2>
    <p>Track revenue trends, peak selling hours and monthly business growth.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Daily Revenue Trend ----------

daily_sales = (
    filtered.groupby(filtered["order_date"].dt.date)["Revenue"]
    .sum()
    .reset_index()
)

fig_daily = px.area(
    daily_sales,
    x="order_date",
    y="Revenue",
    markers=True,
    template="plotly_dark"
)

fig_daily.update_traces(
    line_color="#38BDF8",
    fillcolor="rgba(56,189,248,0.30)"
)

fig_daily.update_layout(
    title="Daily Revenue Trend",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.95)",
    height=430,
    margin=dict(l=20, r=20, t=60, b=20),
    font=dict(color="#E5E7EB"),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,.08)")
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_daily, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# HOUR + MONTH PERFORMANCE
# ======================================================

left, right = st.columns(2)

# ---------- Revenue by Hour ----------

filtered["Hour"] = filtered["order_date"].dt.hour

hourly_sales = (
    filtered.groupby("Hour")["Revenue"]
    .sum()
    .reset_index()
)

fig_hour = px.bar(
    hourly_sales,
    x="Hour",
    y="Revenue",
    template="plotly_dark",
    color="Revenue",
    color_continuous_scale=["#2563EB", "#38BDF8"]
)

fig_hour.update_layout(
    title="Peak Revenue by Hour",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    height=430,
    margin=dict(l=15, r=15, t=55, b=20),
    font=dict(color="#E5E7EB"),
    coloraxis_showscale=False,
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,.08)")
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_hour, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Monthly Revenue ----------

filtered["Month"] = (
    filtered["order_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    filtered.groupby("Month")["Revenue"]
    .sum()
    .reset_index()
)

fig_month = px.line(
    monthly_sales,
    x="Month",
    y="Revenue",
    markers=True,
    template="plotly_dark"
)

fig_month.update_traces(
    line=dict(color="#22D3EE", width=4),
    marker=dict(size=9, color="#2563EB")
)

fig_month.update_layout(
    title="Monthly Revenue Growth",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    height=430,
    margin=dict(l=15, r=15, t=55, b=20),
    font=dict(color="#E5E7EB"),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,.08)")
)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_month, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# SALES PERFORMANCE SUMMARY
# ======================================================

growth_pct = 0
if len(monthly_sales) > 1:
    growth_pct = (
        (monthly_sales.iloc[-1]["Revenue"] -
         monthly_sales.iloc[-2]["Revenue"])
        / monthly_sales.iloc[-2]["Revenue"]
    ) * 100

best_hour = (
    hourly_sales.sort_values("Revenue", ascending=False)
    .iloc[0]["Hour"]
)

best_day = (
    daily_sales.sort_values("Revenue", ascending=False)
    .iloc[0]["order_date"]
)

st.markdown(f"""
<div class="glass-card">

### Sales Performance Summary

- **Peak Selling Hour:** **{int(best_hour):02d}:00**
- **Best Revenue Day:** **{best_day}**
- **Monthly Growth:** **{growth_pct:+.1f}%**
- **Total Revenue in Current Filters:** **₹{revenue:,.0f}**

</div>
""", unsafe_allow_html=True)

# ======================================================
# PRODUCT INTELLIGENCE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Product Intelligence Center</h2>
    <p>Discover category leaders, top-performing brands and product sales contribution.</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# CATEGORY + BRAND PERFORMANCE
# ======================================================

left, right = st.columns(2)

# ---------- CATEGORY REVENUE ----------

category_sales = (
    filtered.groupby("category")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_category = px.bar(
    category_sales,
    x="Revenue",
    y="category",
    orientation="h",
    color="Revenue",
    color_continuous_scale=["#2563EB", "#38BDF8"],
    template="plotly_dark"
)

fig_category.update_layout(
    title="Revenue by Category",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    height=460,
    margin=dict(l=20, r=20, t=60, b=20),
    font=dict(color="#E5E7EB"),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,.08)")
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_category, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- BRAND SHARE ----------

brand_sales = (
    filtered.groupby("brand")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_brand = px.treemap(
    brand_sales,
    path=["brand"],
    values="Revenue",
    color="Revenue",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_brand.update_layout(
    title="Brand Revenue Contribution",
    paper_bgcolor="rgba(0,0,0,0)",
    height=460,
    margin=dict(l=10, r=10, t=60, b=10),
    font=dict(color="#E5E7EB")
)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_brand, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# TOP PRODUCTS vs LOW PRODUCTS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Top & Bottom Product Performance</h2>
    <p>Revenue leaders and underperforming products across the selected filters.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2)

# ---------- TOP PRODUCTS ----------

top_products = (
    filtered.groupby("title")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_top = px.bar(
    top_products,
    x="Revenue",
    y="title",
    orientation="h",
    color="Revenue",
    color_continuous_scale=["#22C55E", "#4ADE80"],
    template="plotly_dark"
)

fig_top.update_layout(
    title="Top 10 Revenue Products",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    height=520,
    margin=dict(l=20, r=20, t=60, b=20),
    font=dict(color="#E5E7EB")
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_top, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- LOW PRODUCTS ----------

bottom_products = (
    filtered.groupby("title")["Revenue"]
    .sum()
    .sort_values()
    .head(10)
    .reset_index()
)

fig_bottom = px.bar(
    bottom_products,
    x="Revenue",
    y="title",
    orientation="h",
    color="Revenue",
    color_continuous_scale=["#EF4444", "#F97316"],
    template="plotly_dark"
)

fig_bottom.update_layout(
    title="Lowest Revenue Products",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    height=520,
    margin=dict(l=20, r=20, t=60, b=20),
    font=dict(color="#E5E7EB")
)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_bottom, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PRODUCT SHARE + INVENTORY INSIGHTS
# ======================================================

left, right = st.columns(2)

# ---------- PRODUCT SHARE DONUT ----------

top_share = (
    filtered.groupby("title")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(6)
    .reset_index()
)

fig_share = px.pie(
    top_share,
    names="title",
    values="Revenue",
    hole=0.65,
    template="plotly_dark"
)

fig_share.update_traces(textinfo="percent+label")

fig_share.update_layout(
    title="Revenue Share of Top Products",
    paper_bgcolor="rgba(0,0,0,0)",
    height=430,
    font=dict(color="#E5E7EB")
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_share, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- INVENTORY ALERT ----------

inventory_summary = (
    filtered.groupby("category")
    .agg(
        Revenue=("Revenue", "sum"),
        Quantity=("quantity", "sum"),
        Rating=("rating", "mean")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    st.markdown("### Category Sales Summary")

    st.dataframe(
        inventory_summary.head(8),
        use_container_width=True,
        height=320
    )

    best_category = inventory_summary.iloc[0]["category"]
    best_revenue = inventory_summary.iloc[0]["Revenue"]

    st.success(
        f"**Top Performing Category:** {best_category}\n\n"
        f"Revenue: ₹{best_revenue:,.0f}"
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER INTELLIGENCE CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Customer Intelligence Center</h2>
    <p>Analyze customer behaviour, geographic demand, payment preferences and retention insights.</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# CUSTOMER KPIs
# ======================================================

repeat_customers = (filtered["customer_id"].value_counts() > 1).sum()
new_customers = (filtered["customer_id"].value_counts() == 1).sum()

top_city = (
    filtered.groupby("city")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .idxmax()
)

avg_customer_value = (
    filtered.groupby("customer_id")["Revenue"]
    .sum()
    .mean()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Repeat Customers", repeat_customers)
c2.metric("New Customers", new_customers)
c3.metric("Top Customer City", top_city)
c4.metric("Avg Customer Value", f"₹{avg_customer_value:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# CITY ANALYTICS
# ======================================================

city_sales = (
    filtered.groupby("city")
    .agg(
        Revenue=("Revenue","sum"),
        Orders=("order_id","nunique")
    )
    .sort_values("Revenue", ascending=False)
    .head(10)
    .reset_index()
)

fig_city = px.bar(
    city_sales,
    x="Revenue",
    y="city",
    orientation="h",
    color="Revenue",
    color_continuous_scale=["#2563EB","#38BDF8"],
    template="plotly_dark"
)

fig_city.update_layout(
    title="Top Revenue Generating Cities",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    height=430,
    font=dict(color="#E5E7EB"),
    margin=dict(l=20,r=20,t=60,b=20)
)

# ======================================================
# CITY REVENUE DONUT
# ======================================================

city_share = city_sales.head(6)

fig_city_share = px.pie(
    city_share,
    names="city",
    values="Revenue",
    hole=.60,
    template="plotly_dark"
)

fig_city_share.update_traces(textinfo="percent+label")

fig_city_share.update_layout(
    title="Revenue Share by City",
    paper_bgcolor="rgba(0,0,0,0)",
    height=430,
    font=dict(color="#E5E7EB")
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_city, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_city_share, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER SEGMENTATION
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Customer Segmentation Analytics</h2>
    <p>Identify loyal, premium and high-value customers using purchase behaviour.</p>
</div>
""", unsafe_allow_html=True)

customer_summary = (
    filtered.groupby("customer_id")
    .agg(
        Orders=("order_id","nunique"),
        Revenue=("Revenue","sum")
    )
    .reset_index()
)

customer_summary["Segment"] = customer_summary["Revenue"].apply(
    lambda x:
        "VIP" if x >= 12000 else
        "Premium" if x >= 7000 else
        "Regular"
)

segment_df = (
    customer_summary.groupby("Segment")
    .size()
    .reset_index(name="Customers")
)

fig_segment = px.pie(
    segment_df,
    names="Segment",
    values="Customers",
    hole=.55,
    color="Segment",
    color_discrete_map={
        "VIP":"#22C55E",
        "Premium":"#2563EB",
        "Regular":"#64748B"
    },
    template="plotly_dark"
)

fig_segment.update_layout(
    title="Customer Segments",
    paper_bgcolor="rgba(0,0,0,0)",
    height=390,
    font=dict(color="#E5E7EB")
)

top_customers = (
    customer_summary.sort_values("Revenue", ascending=False)
    .head(10)
)

fig_customer = px.bar(
    top_customers,
    x="Revenue",
    y="customer_id",
    orientation="h",
    color="Revenue",
    color_continuous_scale=["#22C55E","#4ADE80"],
    template="plotly_dark"
)

fig_customer.update_layout(
    title="Top High Value Customers",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    height=390,
    font=dict(color="#E5E7EB")
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_segment, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_customer, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PAYMENT ANALYTICS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Payment Intelligence</h2>
    <p>Monitor customer payment preferences and revenue contribution.</p>
</div>
""", unsafe_allow_html=True)

payment_df = (
    filtered.groupby("payment_method")
    .agg(
        Orders=("order_id","count"),
        Revenue=("Revenue","sum")
    )
    .reset_index()
)

fig_payment_bar = px.bar(
    payment_df,
    x="payment_method",
    y="Revenue",
    color="Revenue",
    color_continuous_scale=["#2563EB","#22D3EE"],
    template="plotly_dark"
)

fig_payment_bar.update_layout(
    title="Revenue by Payment Method",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    coloraxis_showscale=False,
    height=360,
    font=dict(color="#E5E7EB")
)

fig_payment_donut = px.pie(
    payment_df,
    names="payment_method",
    values="Orders",
    hole=.55,
    template="plotly_dark"
)

fig_payment_donut.update_layout(
    title="Payment Method Share",
    paper_bgcolor="rgba(0,0,0,0)",
    height=360,
    font=dict(color="#E5E7EB")
)

pay1, pay2 = st.columns(2)

with pay1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_payment_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with pay2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_payment_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER LEADERBOARD
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Customer Leaderboard</h2>
    <p>Highest spending customers and latest customer transactions.</p>
</div>
""", unsafe_allow_html=True)

leader1, leader2 = st.columns(2)

recent_orders = (
    filtered.sort_values("order_date", ascending=False)
    [["customer_id","city","payment_method","Revenue","order_date"]]
    .head(12)
)

with leader1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("#### Recent Customer Orders")
    st.dataframe(
        recent_orders,
        use_container_width=True,
        height=340
    )
    st.markdown("</div>", unsafe_allow_html=True)

with leader2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("#### Highest Spending Customers")
    st.dataframe(
        top_customers.rename(columns={"Revenue":"Lifetime Revenue"}),
        use_container_width=True,
        height=340
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# SALES INSIGHTS CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Sales Insights Center</h2>
    <p>Discover peak selling days, hourly demand patterns and category-brand performance.</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# CATEGORY × BRAND MATRIX
# ======================================================

matrix = filtered.pivot_table(
    values="Revenue",
    index="category",
    columns="brand",
    aggfunc="sum",
    fill_value=0
)

fig_matrix = px.imshow(
    matrix,
    text_auto=True,
    aspect="auto",
    color_continuous_scale=[
        "#0F172A",
        "#1D4ED8",
        "#2563EB",
        "#38BDF8"
    ]
)

fig_matrix.update_layout(
    title="Category vs Brand Revenue Matrix",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB"),
    height=480,
    margin=dict(l=20,r=20,t=60,b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_matrix, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# WEEKDAY × HOUR SALES HEATMAP
# ======================================================

filtered["Weekday"] = filtered["order_date"].dt.day_name()
filtered["Hour"] = filtered["order_date"].dt.hour

weekday_order = [
    "Monday","Tuesday","Wednesday",
    "Thursday","Friday","Saturday","Sunday"
]

heat = (
    filtered.groupby(["Weekday","Hour"])["Revenue"]
    .sum()
    .reset_index()
)

heat["Weekday"] = pd.Categorical(
    heat["Weekday"],
    categories=weekday_order,
    ordered=True
)

pivot = (
    heat.pivot(index="Weekday", columns="Hour", values="Revenue")
    .fillna(0)
)

fig_heat = px.imshow(
    pivot,
    aspect="auto",
    text_auto=True,
    color_continuous_scale="Viridis"
)

fig_heat.update_layout(
    title="Weekly Sales Heatmap (Revenue by Hour)",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#E5E7EB"),
    height=470,
    margin=dict(l=20,r=20,t=60,b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_heat, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# LIVE SALES TRANSACTION CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Sales Transaction Center</h2>
    <p>Monitor recent orders, customer activity and inventory alerts in real time.</p>
</div>
""", unsafe_allow_html=True)

live1, live2 = st.columns([1.5,1])

recent_sales = (
    filtered.sort_values("order_date", ascending=False)
    [[
        "order_id",
        "order_date",
        "title",
        "brand",
        "city",
        "quantity",
        "Revenue",
        "payment_method"
    ]]
    .head(15)
)

with live1:

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("### Recent Sales Activity")

    st.dataframe(
        recent_sales,
        use_container_width=True,
        height=390
    )

    st.markdown("</div>", unsafe_allow_html=True)

inventory_alert = (
    filtered.groupby(["title","brand"])
    .agg(
        Quantity=("quantity","sum"),
        Revenue=("Revenue","sum")
    )
    .sort_values("Quantity", ascending=False)
    .head(10)
    .reset_index()
)

with live2:

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("### Best Selling Inventory")

    st.dataframe(
        inventory_alert,
        use_container_width=True,
        height=390
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# SALES SUMMARY CARD
# ======================================================

top_category = category_sales.iloc[0]["category"]
top_brand = brand_sales.sort_values("Revenue", ascending=False).iloc[0]["brand"]

best_product = top_products.iloc[0]["title"]
best_product_revenue = top_products.iloc[0]["Revenue"]

st.markdown(f"""
<div class="glass-card">

### Executive Sales Summary

**Revenue Generated:** ₹{revenue:,.0f}

**Orders Processed:** {orders_count:,}

**Products Sold:** {int(products_sold):,}

**Top Category:** {top_category}

**Top Brand:** {top_brand}

**Best Selling Product:** {best_product}

**Product Revenue:** ₹{best_product_revenue:,.0f}

**Cities Served:** {cities_count}

</div>
""", unsafe_allow_html=True)

# ======================================================
# EXPORT CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Sales Export Center</h2>
    <p>Download filtered enterprise sales data for Excel, Power BI and business reporting.</p>
</div>
""", unsafe_allow_html=True)

csv = filtered.to_csv(index=False).encode("utf-8")

st.markdown("<div class='download-card'>", unsafe_allow_html=True)

st.markdown("### Download Filtered Sales Report")
st.markdown(
    "Export complete filtered sales transactions with product, customer, revenue and payment analytics."
)

st.download_button(
    label="Download Sales Analytics Report (CSV)",
    data=csv,
    file_name="CommerceIQ_Sales_Analytics_Report.csv",
    mime="text/csv",
    use_container_width=True
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-premium">

## CommerceIQ Sales Intelligence Suite

Enterprise Sales Analytics • Revenue Intelligence • Customer Intelligence • Power BI Ready Reporting

**Built with Streamlit • PostgreSQL • Plotly • Pandas • SQLAlchemy**

</div>
""", unsafe_allow_html=True)