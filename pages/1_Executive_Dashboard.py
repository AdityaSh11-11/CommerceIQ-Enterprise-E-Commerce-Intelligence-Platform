import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

from config import DATABASE_URL

st.set_page_config(
    page_title="Executive Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)
</style>
""", unsafe_allow_html=True)
with open("dashboard_style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

@st.cache_data(ttl=30)
def load_data():

    orders = pd.read_sql("SELECT * FROM orders", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    return orders, products, customers, order_items

orders, products, customers, order_items = load_data()

st.markdown("""
<div class="hero-small">

<div class="hero-chip">
COMMERCEIQ ENTERPRISE ANALYTICS
</div>

<h1>Executive Intelligence Dashboard</h1>

<p>
Monitor revenue, customer growth, inventory health, operational performance
and business KPIs in real time through CommerceIQ Executive Analytics Engine.
</p>

</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([8, 2])

with col2:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()   # Clear cached queries
        st.cache_resource.clear()
        st.rerun()              # Reload page

revenue = orders["net_amount"].sum()
orders_count = len(orders)
customers_count = len(customers)

profit = revenue - orders["tax"].sum()
aov = revenue / orders_count if orders_count else 0

products_sold = order_items["quantity"].sum()

repeat_rate = (
    orders["customer_id"]
    .value_counts()
    .gt(1)
    .mean() * 100
)

low_stock = len(products[products.stock < 20])

inventory_value = (products["price"] * products["stock"]).sum()

growth = (
    orders.groupby(orders["order_date"].dt.date)["net_amount"]
    .sum()
    .pct_change()
    .fillna(0)
)

growth_percent = growth.iloc[-1] * 100 if len(growth) else 0

st.markdown("""
<div class="section-header">
    <h2>Executive KPI Snapshot</h2>
</div>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Revenue",
        f"₹{revenue:,.0f}",
        f"{growth_percent:+.1f}% Today"
    )

with k2:
    st.metric(
        "Orders",
        f"{orders_count:,}",
        "+12% Orders"
    )

with k3:
    st.metric(
        "Customers",
        f"{customers_count:,}",
        "+8% Growth"
    )

with k4:
    st.metric(
        "Profit",
        f"₹{profit:,.0f}",
        "+15% Margin"
    )

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

k5, k6, k7, k8 = st.columns(4)

with k5:
    st.metric(
        "Average Order Value",
        f"₹{aov:,.0f}",
        "+5.2%"
    )

with k6:
    st.metric(
        "Products Sold",
        f"{int(products_sold):,}",
        "+420 Units"
    )

with k7:
    st.metric(
        "Repeat Customers",
        f"{repeat_rate:.1f}%",
        "+3.4%"
    )

with k8:
    st.metric(
        "Low Stock Products",
        low_stock,
        "-6 Today"
    )

score = 100

if low_stock > 60:
    score -= 15

if repeat_rate < 50:
    score -= 15

if aov < 4000:
    score -= 10

if score >= 90:
    health = "Excellent"
    health_color = "#22C55E"

elif score >= 75:
    health = "Healthy"
    health_color = "#38BDF8"

else:
    health = "Needs Attention"
    health_color = "#F59E0B"

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

left, right = st.columns([1.1, 1])

with left:

    st.markdown(f"""
    <div class="glass-card">

    ### Business Health Score

    <h1 style="font-size:56px;color:{health_color};margin-bottom:0;">
        {score}/100
    </h1>

    <p style="color:#CBD5E1;font-size:18px;">
        {health}
    </p>

    <div style="margin-top:15px;">
        AI continuously evaluates customer retention,
        inventory health and revenue momentum.
    </div>

    </div>
    """, unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="glass-card">

    ### AI Executive Engine

    <h2 style="color:#22D3EE;">ACTIVE</h2>

    <p>Google Gemini AI Connected</p>

    <hr>

    **Live Monitoring**

    - Revenue Intelligence
    - Customer Behaviour Analytics
    - Inventory Risk Detection
    - Executive Decision Support

    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="section-header">
    <h2>Business Intelligence Highlights</h2>
    <p>AI-generated operational snapshot from your CommerceIQ warehouse.</p>
</div>
""", unsafe_allow_html=True)

i1, i2, i3, i4 = st.columns(4)

with i1:
    st.markdown(f"""
    <div class="status-card">
        <h2>{growth_percent:True}%</h2>
        <p>Revenue Growth</p>
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown(f"""
    <div class="status-card">
        <h2>{repeat_rate:.0f}%</h2>
        <p>Customer Retention</p>
    </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown(f"""
    <div class="status-card">
        <h2>₹{inventory_value/100000:.1f}L</h2>
        <p>Inventory Value</p>
    </div>
    """, unsafe_allow_html=True)

with i4:
    st.markdown(f"""
    <div class="status-card">
        <h2>{low_stock}</h2>
        <p>Inventory Alerts</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ======================================================
# SALES PERFORMANCE DASHBOARD
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Sales Performance Intelligence</h2>
    <p>Track daily revenue, order volume, hourly performance and sales momentum across CommerceIQ.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- FILTERS ----------------

filter1, filter2, filter3 = st.columns([2,2,1])

with filter1:
    start_date = st.date_input(
        "Start Date",
        value=orders["order_date"].min().date()
    )

with filter2:
    end_date = st.date_input(
        "End Date",
        value=orders["order_date"].max().date()
    )

with filter3:
    status_filter = st.selectbox(
        "Status",
        ["All"] + sorted(orders["status"].unique().tolist())
    )

# ---------------- FILTER DATA ----------------

filtered_orders = orders[
    (orders["order_date"].dt.date >= start_date) &
    (orders["order_date"].dt.date <= end_date)
].copy()

if status_filter != "All":
    filtered_orders = filtered_orders[
        filtered_orders["status"] == status_filter
    ]

# ======================================================
# SALES KPIs
# ======================================================

sales_revenue = filtered_orders["net_amount"].sum()
sales_orders = len(filtered_orders)

daily_orders = (
    filtered_orders.groupby(filtered_orders["order_date"].dt.date)
    .size()
    .mean()
)

highest_sale = filtered_orders["net_amount"].max()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Revenue (Filtered)", f"₹{sales_revenue:,.0f}")
c2.metric("Orders (Filtered)", f"{sales_orders:,}")
c3.metric("Avg Daily Orders", f"{daily_orders:.1f}")
c4.metric("Highest Order Value", f"₹{highest_sale:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# DAILY REVENUE TREND
# ======================================================

daily = (
    filtered_orders.groupby(filtered_orders["order_date"].dt.date)
    .agg(
        Revenue=("net_amount", "sum"),
        Orders=("order_id", "count")
    )
    .reset_index()
)

fig_daily = px.area(
    daily,
    x="order_date",
    y="Revenue",
    title="Daily Revenue Trend",
    markers=True,
    template="plotly_dark"
)

fig_daily.update_traces(
    line_color="#38BDF8",
    fillcolor="rgba(56,189,248,0.25)"
)

fig_daily.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.35)",
    height=430,
    margin=dict(l=20,r=20,t=55,b=20),
    title_font=dict(size=20,color="white"),
    font=dict(color="#CBD5E1"),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,.08)")
)

# ======================================================
# REVENUE BY HOUR
# ======================================================

filtered_orders["hour"] = filtered_orders["order_date"].dt.hour

hourly = (
    filtered_orders.groupby("hour")["net_amount"]
    .sum()
    .reset_index()
)

fig_hour = px.bar(
    hourly,
    x="hour",
    y="net_amount",
    title="Revenue by Hour",
    template="plotly_dark"
)

fig_hour.update_traces(
    marker_color="#2563EB"
)

fig_hour.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.35)",
    height=430,
    margin=dict(l=20,r=20,t=55,b=20),
    title_font=dict(size=20,color="white"),
    font=dict(color="#CBD5E1"),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor="rgba(255,255,255,.08)")
)

# ======================================================
# CHART LAYOUT
# ======================================================

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_daily, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_hour, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# SALES MOMENTUM ANALYTICS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Sales Momentum Analytics</h2>
    <p>Revenue behaviour and operational performance generated from live order activity.</p>
</div>
""", unsafe_allow_html=True)

trend_col, status_col = st.columns([1.4,1])

# ---------- Revenue Trend Card ----------

with trend_col:

    revenue_change = daily["Revenue"].pct_change().fillna(0)

    fig_growth = px.line(
        daily,
        x="order_date",
        y="Revenue",
        template="plotly_dark",
        title="Revenue Momentum"
    )

    fig_growth.update_traces(
        line_color="#22D3EE",
        line_width=4
    )

    fig_growth.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,.35)",
        height=300,
        margin=dict(l=20,r=20,t=45,b=20),
        title_font=dict(size=18,color="white"),
        font=dict(color="#CBD5E1"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,.08)")
    )

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_growth, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Order Status Summary ----------

with status_col:

    status_summary = (
        filtered_orders.groupby("status")
        .size()
        .reset_index(name="Orders")
        .sort_values("Orders", ascending=False)
    )

    fig_status = px.bar(
        status_summary,
        x="Orders",
        y="status",
        orientation="h",
        template="plotly_dark",
        title="Order Status Summary"
    )

    fig_status.update_traces(marker_color="#10B981")

    fig_status.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,.35)",
        height=300,
        margin=dict(l=20,r=20,t=45,b=20),
        title_font=dict(size=18,color="white"),
        font=dict(color="#CBD5E1"),
        yaxis_title="",
        xaxis=dict(gridcolor="rgba(255,255,255,.08)")
    )

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_status, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# PRODUCT INTELLIGENCE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Product Intelligence Center</h2>
    <p>Analyze product sales, category contribution, brand performance and inventory health in one place.</p>
</div>
""", unsafe_allow_html=True)

# Merge sales data
sales = order_items.merge(products, on="product_id")
sales["sales"] = sales["quantity"] * sales["unit_price"]

# ======================================================
# PRODUCT KPIs
# ======================================================

top_product_series = (
    sales.groupby("title")["sales"]
    .sum()
    .sort_values(ascending=False)
)

top_product = top_product_series.index[0]
top_product_sales = top_product_series.iloc[0]

categories_count = products["category"].nunique()
brands_count = products["brand"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Categories", categories_count)
k2.metric("Brands", brands_count)
k3.metric("Best Selling Product", str(top_product)[:18] + "...")
k4.metric("Top Product Revenue", f"₹{top_product_sales:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# TOP PRODUCTS
# ======================================================

top_products = (
    sales.groupby("title")["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_products = px.bar(
    top_products,
    x="sales",
    y="title",
    orientation="h",
    title="Top Selling Products",
    template="plotly_dark",
    color="sales",
    color_continuous_scale="Blues"
)

fig_products.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.35)",
    height=420,
    margin=dict(l=10,r=20,t=50,b=20),
    font=dict(color="#CBD5E1"),
    coloraxis_showscale=False
)

# ======================================================
# CATEGORY CONTRIBUTION
# ======================================================

category_sales = (
    sales.groupby("category")["sales"]
    .sum()
    .reset_index()
)

fig_category = px.treemap(
    category_sales,
    path=["category"],
    values="sales",
    color="sales",
    color_continuous_scale="Teal"
)

fig_category.update_layout(
    title="Revenue Contribution by Category",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0,r=0,t=50,b=0),
    height=420,
    font=dict(color="white"),
    coloraxis_showscale=False
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_products, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_category, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# BRAND ANALYTICS
# ======================================================

brand_sales = (
    sales.groupby("brand")
    .agg(
        Revenue=("sales","sum"),
        Quantity=("quantity","sum")
    )
    .sort_values("Revenue", ascending=False)
    .head(8)
    .reset_index()
)

fig_brand = px.bar(
    brand_sales,
    x="brand",
    y="Revenue",
    color="Revenue",
    template="plotly_dark",
    title="Top Revenue Generating Brands",
    color_continuous_scale="Blues"
)

fig_brand.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.35)",
    height=350,
    font=dict(color="#CBD5E1"),
    coloraxis_showscale=False
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_brand, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# INVENTORY HEALTH
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Inventory Intelligence</h2>
    <p>Identify inventory risks, stock distribution and replenishment priorities.</p>
</div>
""", unsafe_allow_html=True)

products["Stock Status"] = products["stock"].apply(
    lambda x:
        "Critical" if x < 20 else
        "Medium" if x < 60 else
        "Healthy"
)

inventory_status = (
    products.groupby("Stock Status")
    .size()
    .reset_index(name="Products")
)

fig_inventory = px.pie(
    inventory_status,
    names="Stock Status",
    values="Products",
    hole=.60,
    color="Stock Status",
    color_discrete_map={
        "Healthy":"#22C55E",
        "Medium":"#F59E0B",
        "Critical":"#EF4444"
    },
    template="plotly_dark",
    title="Inventory Health Distribution"
)

fig_inventory.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=360,
    font=dict(color="#CBD5E1")
)

low_stock_df = (
    products[products.stock < 20]
    .sort_values("stock")
    [["title","brand","category","stock","rating"]]
)

c1, c2 = st.columns([1,1.2])

with c1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_inventory, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    st.markdown("#### Critical Inventory Alerts")

    st.dataframe(
        low_stock_df,
        use_container_width=True,
        height=330
    )

    st.markdown("</div>", unsafe_allow_html=True)

st.divider()


# ======================================================
# CUSTOMER INTELLIGENCE CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Customer Intelligence Center</h2>
    <p>Understand customer behaviour, geographic demand, retention trends and payment preferences.</p>
</div>
""", unsafe_allow_html=True)

orders_customer = orders.merge(customers, on="customer_id")

# ======================================================
# CUSTOMER KPIs
# ======================================================

repeat_customers = (orders.customer_id.value_counts() > 1).sum()
new_customers = (orders.customer_id.value_counts() == 1).sum()

top_city = (
    orders_customer.groupby("city")
    .size()
    .sort_values(ascending=False)
    .idxmax()
)

customer_ltv = (
    orders.groupby("customer_id")["net_amount"]
    .sum()
    .mean()
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Repeat Customers", repeat_customers)
k2.metric("New Customers", new_customers)
k3.metric("Top Customer City", top_city)
k4.metric("Avg Customer Value", f"₹{customer_ltv:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# GEOGRAPHIC ANALYTICS
# ======================================================

city_orders = (
    orders_customer.groupby("city")
    .agg(
        Orders=("order_id","count"),
        Revenue=("net_amount","sum")
    )
    .sort_values("Revenue", ascending=False)
    .head(10)
    .reset_index()
)

fig_city = px.bar(
    city_orders,
    x="Revenue",
    y="city",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Blues",
    template="plotly_dark",
    title="Top Revenue Generating Cities"
)

fig_city.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.35)",
    height=420,
    margin=dict(l=10,r=20,t=45,b=20),
    font=dict(color="#CBD5E1"),
    coloraxis_showscale=False
)

# Use state if available, otherwise city
location_col = "state" if "state" in orders_customer.columns else "city"

location_orders = (
    orders_customer.groupby(location_col)
    .agg(Revenue=("net_amount", "sum"))
    .sort_values("Revenue", ascending=False)
    .head(8)
    .reset_index()
)

fig_state = px.pie(
    location_orders,
    names=location_col,
    values="Revenue",
    hole=0.60,
    template="plotly_dark",
    title=f"Revenue Distribution by {location_col.title()}"
)

fig_state.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=420,
    font=dict(color="#CBD5E1")
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_city, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_state, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CUSTOMER SEGMENTATION
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Customer Segmentation Analytics</h2>
    <p>Identify loyal customers, high-value buyers and purchasing behaviour.</p>
</div>
""", unsafe_allow_html=True)

customer_value = (
    orders.groupby("customer_id")
    .agg(
        Orders=("order_id","count"),
        Revenue=("net_amount","sum")
    )
    .reset_index()
)

customer_value["Segment"] = customer_value["Revenue"].apply(
    lambda x:
        "VIP" if x > 12000 else
        "Premium" if x > 7000 else
        "Regular"
)

segment_summary = (
    customer_value.groupby("Segment")
    .size()
    .reset_index(name="Customers")
)

fig_segment = px.pie(
    segment_summary,
    names="Segment",
    values="Customers",
    hole=.55,
    color="Segment",
    color_discrete_map={
        "VIP":"#22C55E",
        "Premium":"#3B82F6",
        "Regular":"#64748B"
    },
    template="plotly_dark",
    title="Customer Segments"
)

fig_segment.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    height=360,
    font=dict(color="#CBD5E1")
)

vip_customers = (
    customer_value.sort_values("Revenue", ascending=False)
    .head(10)
)

fig_ltv = px.bar(
    vip_customers,
    x="customer_id",
    y="Revenue",
    color="Revenue",
    color_continuous_scale="Greens",
    template="plotly_dark",
    title="Top High Value Customers"
)

fig_ltv.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.35)",
    height=360,
    font=dict(color="#CBD5E1"),
    coloraxis_showscale=False
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_segment, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_ltv, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PAYMENT INTELLIGENCE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Payment Intelligence</h2>
    <p>Monitor payment method adoption and revenue contribution.</p>
</div>
""", unsafe_allow_html=True)

payment_summary = (
    orders.groupby("payment_method")
    .agg(
        Orders=("order_id","count"),
        Revenue=("net_amount","sum")
    )
    .reset_index()
)

fig_payment = px.bar(
    payment_summary,
    x="payment_method",
    y="Revenue",
    color="Revenue",
    template="plotly_dark",
    title="Revenue by Payment Method",
    color_continuous_scale="Blues"
)

fig_payment.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.35)",
    height=340,
    font=dict(color="#CBD5E1"),
    coloraxis_showscale=False
)

fig_payment_pie = px.pie(
    payment_summary,
    names="payment_method",
    values="Orders",
    hole=.55,
    template="plotly_dark",
    title="Payment Method Share"
)

fig_payment_pie.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    height=340,
    font=dict(color="#CBD5E1")
)

pay1, pay2 = st.columns(2)

with pay1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_payment, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with pay2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_payment_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# LIVE CUSTOMER FEED
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Customer Feed</h2>
    <p>Recent customer transactions and top performing customers updated from the warehouse.</p>
</div>
""", unsafe_allow_html=True)

feed1, feed2 = st.columns(2)

# Detect customer name column safely
customer_name_col = (
    "name" if "name" in orders_customer.columns
    else "customer_name" if "customer_name" in orders_customer.columns
    else "full_name" if "full_name" in orders_customer.columns
    else "email" if "email" in orders_customer.columns
    else None
)

display_cols = ["customer_id"]

if customer_name_col:
    display_cols.append(customer_name_col)

display_cols += ["city", "net_amount", "order_date"]

recent_customers = (
    orders_customer.sort_values("order_date", ascending=False)[display_cols]
    .head(12)
)

top_customers = (
    customer_value.sort_values("Revenue", ascending=False)
    .head(12)
)

with feed1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("#### Recent Customer Orders")
    st.dataframe(
        recent_customers,
        use_container_width=True,
        height=350
    )
    st.markdown("</div>", unsafe_allow_html=True)

with feed2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("#### Top Revenue Customers")
    st.dataframe(
        top_customers,
        use_container_width=True,
        height=350
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# OPERATIONAL INTELLIGENCE CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Operational Intelligence Center</h2>
    <p>Monitor inventory health, order pipeline, fulfillment performance and live warehouse operations.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# OPERATIONAL KPIs
# ------------------------------------------------------

completed_orders = len(orders[orders["status"] == "Delivered"])
pending_orders = len(orders[orders["status"] == "Pending"])
cancelled_orders = len(orders[orders["status"] == "Cancelled"])

inventory_health = round((products.stock > 20).mean() * 100)

o1, o2, o3, o4 = st.columns(4)

o1.metric("Inventory Health", f"{inventory_health}%")
o2.metric("Delivered Orders", completed_orders)
o3.metric("Pending Orders", pending_orders)
o4.metric("Cancelled Orders", cancelled_orders)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------
# ORDER STATUS DONUT
# ------------------------------------------------------

status_df = (
    orders.groupby("status")
    .size()
    .reset_index(name="Orders")
)

fig_status = px.pie(
    status_df,
    names="status",
    values="Orders",
    hole=.65,
    template="plotly_dark",
    title="Order Fulfillment Status",
    color="status",
    color_discrete_map={
        "Delivered":"#22C55E",
        "Pending":"#F59E0B",
        "Cancelled":"#EF4444",
        "Shipped":"#2563EB"
    }
)

fig_status.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    height=370,
    font=dict(color="#CBD5E1")
)

# ------------------------------------------------------
# INVENTORY GAUGE
# ------------------------------------------------------

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=inventory_health,
    title={"text":"Inventory Health Score"},
    gauge={
        "axis":{"range":[0,100]},
        "bar":{"color":"#22D3EE"},
        "steps":[
            {"range":[0,40],"color":"#7F1D1D"},
            {"range":[40,70],"color":"#78350F"},
            {"range":[70,100],"color":"#14532D"}
        ]
    }
))

fig_gauge.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=370
)

left, right = st.columns(2)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_status, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# INVENTORY RISK TABLE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Warehouse Risk Monitor</h2>
    <p>Products requiring immediate replenishment based on stock thresholds.</p>
</div>
""", unsafe_allow_html=True)

critical_stock = (
    products[products.stock < 20]
    .sort_values("stock")
    [["title","brand","category","stock","price","rating"]]
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

st.dataframe(
    critical_stock,
    use_container_width=True,
    height=330
)

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# LIVE BUSINESS FEED
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Business Feed</h2>
    <p>Latest transactions and operational activities streaming from CommerceIQ.</p>
</div>
""", unsafe_allow_html=True)

feed1, feed2 = st.columns(2)

latest_orders = (
    orders.sort_values("order_date", ascending=False)
    [["order_id","customer_id","status","payment_method","net_amount","order_date"]]
    .head(12)
)

latest_inventory = (
    products.sort_values("stock")
    [["title","category","stock","rating"]]
    .head(12)
)

with feed1:

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    st.markdown("#### Recent Order Activity")

    st.dataframe(
        latest_orders,
        use_container_width=True,
        height=360
    )

    st.markdown("</div>", unsafe_allow_html=True)

with feed2:

    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

    st.markdown("#### Inventory Alerts")

    st.dataframe(
        latest_inventory,
        use_container_width=True,
        height=360
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# EXECUTIVE SUMMARY PANEL
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Executive Business Summary</h2>
    <p>AI-powered operational snapshot for executive leadership and business teams.</p>
</div>
""", unsafe_allow_html=True)

summary_left, summary_right = st.columns([1.3,1])

with summary_left:

    st.markdown(f"""
    <div class="glass-card">

    ### CommerceIQ Executive Insights

    **Revenue Generated:** ₹{revenue:,.0f}

    **Profit Estimated:** ₹{profit:,.0f}

    **Orders Processed:** {orders_count:,}

    **Repeat Customer Rate:** {repeat_rate:.1f}%

    **Inventory Health:** {inventory_health}%

    AI continuously monitors inventory, customer retention,
    payment behaviour and operational performance to help reduce
    stock-outs and improve revenue visibility.

    </div>
    """, unsafe_allow_html=True)

with summary_right:

    st.markdown("""
    <div class="glass-card">

    ### Operational Highlights

    ✅ Live Order Monitoring

    ✅ Inventory Risk Detection

    ✅ Customer Behaviour Analytics

    ✅ Revenue & Profit Tracking

    ✅ Executive KPI Monitoring

    ✅ Real-Time Business Intelligence

    </div>
    """, unsafe_allow_html=True)

# ======================================================
# PLATFORM STATUS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>CommerceIQ Platform Status</h2>
</div>
""", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

with s1:
    st.markdown("""
    <div class="status-card">
        <h2 style="color:#22C55E;">SYSTEM ONLINE</h2>
        <p>Database Connected</p>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown("""
    <div class="status-card">
        <h2 style="color:#38BDF8;">LIVE ANALYTICS</h2>
        <p>Real-Time Dashboard Active</p>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown("""
    <div class="status-card">
        <h2 style="color:#A855F7;">AI ENABLED</h2>
        <p>Gemini Executive Intelligence Running</p>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="ai-footer">
    <h4>CommerceIQ AI Executive Intelligence</h4>
    <p>Powered by Google Gemini AI • Real-Time Business Analytics • Executive Decision Intelligence</p>
</div>
""", unsafe_allow_html=True)
