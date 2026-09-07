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
    page_title="Product Analytics Dashboard",
    page_icon="📦",
    layout="wide"
)

with open("dashboard_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=15)
def load_data():

    products = pd.read_sql("SELECT * FROM products", engine)
    orders = pd.read_sql("SELECT * FROM orders", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    sales = order_items.merge(products, on="product_id")
    sales["Revenue"] = sales["quantity"] * sales["unit_price"]

    return products, orders, sales


products, orders, sales = load_data()

# ======================================================
# HERO SECTION
# ======================================================

st.markdown("""
<div class="hero-small">
    <div class="hero-chip">COMMERCEIQ PRODUCT INTELLIGENCE</div>

    <h1>Product Analytics Dashboard</h1>

    <p>
        Monitor inventory health, product demand, stock availability,
        category performance and revenue contribution with real-time
        executive product intelligence.
    </p>
</div>
""", unsafe_allow_html=True)

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
# KPI CALCULATIONS
# ======================================================

total_products = len(products)

inventory_value = (products["price"] * products["stock"]).sum()

units_sold = sales["quantity"].sum()

low_stock = int((products["stock"] < 20).sum())

out_of_stock = int((products["stock"] <= 0).sum())

avg_rating = products["rating"].mean()

categories = products["category"].nunique()

brands = products["brand"].nunique()

healthy_stock = int((products["stock"] >= 20).sum())

# ======================================================
# EXECUTIVE KPI SECTION
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Product Intelligence Overview</h2>
    <p>Enterprise snapshot of inventory performance, warehouse health and product sales metrics.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Row 1 ----------

row1 = st.columns(4)

with row1[0]:
    st.metric("📦 Total Products", f"{total_products:,}")

with row1[1]:
    st.metric("💰 Inventory Value", f"₹{inventory_value:,.0f}")

with row1[2]:
    st.metric("🛒 Units Sold", f"{int(units_sold):,}")

with row1[3]:
    st.metric("⭐ Average Rating", f"{avg_rating:.1f}")

# ---------- Row 2 ----------

row2 = st.columns(4)

with row2[0]:
    st.metric("⚠️ Low Stock Items", low_stock)

with row2[1]:
    st.metric("❌ Out of Stock", out_of_stock)

with row2[2]:
    st.metric("🧩 Categories", categories)

with row2[3]:
    st.metric("🏷️ Brands", brands)

st.divider()

# ======================================================
# INVENTORY EXECUTIVE SNAPSHOT
# ======================================================

with st.container(border=True):

    st.subheader("📊 Inventory Executive Snapshot")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Healthy Inventory", healthy_stock)

    with c2:
        st.metric("Low Stock Products", low_stock)

    with c3:
        st.metric("Out of Stock Products", out_of_stock)

    st.info(
        "CommerceIQ continuously monitors inventory availability, stock shortages, warehouse utilization and product demand to improve replenishment planning."
    )

st.divider()

# ======================================================
# INVENTORY HEALTH OVERVIEW
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Inventory Health Overview</h2>
    <p>Track inventory availability, stock shortages and warehouse health across all products.</p>
</div>
""", unsafe_allow_html=True)

inventory = products.copy()

inventory["Status"] = inventory["stock"].apply(
    lambda x: "Out of Stock"
    if x <= 0
    else "Low Stock"
    if x < 20
    else "Healthy"
)

left, right = st.columns(2)

# ------------------------------------------------------
# Inventory Distribution
# ------------------------------------------------------

fig_inventory = px.pie(
    inventory,
    names="Status",
    hole=0.60,
    color="Status",
    color_discrete_map={
        "Healthy": "#10B981",
        "Low Stock": "#F59E0B",
        "Out of Stock": "#EF4444"
    },
    template="plotly_dark"
)

fig_inventory.update_layout(
    title="Inventory Distribution",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    legend=dict(
        orientation="h",
        y=-0.15,
        font=dict(color="#CBD5E1")
    ),
    margin=dict(l=10, r=10, t=60, b=30)
)

# ------------------------------------------------------
# Inventory Health Score
# ------------------------------------------------------

health_score = round((products["stock"] >= 20).mean() * 100)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=health_score,
    title={"text": "Inventory Health Score"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "#22D3EE"},
        "steps": [
            {"range": [0, 40], "color": "#7F1D1D"},
            {"range": [40, 70], "color": "#92400E"},
            {"range": [70, 100], "color": "#064E3B"}
        ]
    }
))

fig_gauge.update_layout(
    template="plotly_dark",
    height=420,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=30)
)

# ------------------------------------------------------
# Render Cards
# ------------------------------------------------------

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_inventory, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# INVENTORY SNAPSHOT CARD
# ======================================================

healthy_products = int((products["stock"] >= 20).sum())

with st.container(border=True):

    st.subheader("📦 Inventory Snapshot")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Healthy Products", healthy_products)

    with c2:
        st.metric("Low Stock Products", low_stock)

    with c3:
        st.metric("Out of Stock Products", out_of_stock)

    st.info(
        "CommerceIQ AI continuously monitors inventory availability, stock shortages and warehouse utilization to improve replenishment planning and reduce stock-out risk."
    )

st.divider()

# ======================================================
# CATEGORY & BRAND PERFORMANCE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Category & Brand Performance</h2>
    <p>Compare revenue contribution, units sold and brand-wise business performance across product categories.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2)

# ------------------------------------------------------
# Category Revenue Performance
# ------------------------------------------------------

category_sales = (
    sales.groupby("category")
    .agg(
        Revenue=("Revenue", "sum"),
        Units=("quantity", "sum")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

fig_category = px.bar(
    category_sales,
    x="Revenue",
    y="category",
    orientation="h",
    color="Revenue",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_category.update_layout(
    title="Revenue by Category",
    height=450,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    coloraxis_showscale=False,
    margin=dict(l=10, r=10, t=60, b=20)
)

# ------------------------------------------------------
# Brand Revenue Treemap
# ------------------------------------------------------

brand_sales = (
    sales.groupby("brand")
    .agg(
        Revenue=("Revenue", "sum"),
        Units=("quantity", "sum")
    )
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
    height=450,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC"),
    coloraxis_showscale=False,
    margin=dict(l=5, r=5, t=55, b=10)
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_category, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_brand, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# CATEGORY EXECUTIVE SUMMARY
# ======================================================

top_category = category_sales.iloc[0]
top_brand = brand_sales.sort_values("Revenue", ascending=False).iloc[0]

with st.container(border=True):

    st.subheader("🏷️ Category Executive Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Top Revenue Category", top_category["category"])
        st.metric(
            "Category Revenue",
            f"₹{top_category['Revenue']:,.0f}"
        )

    with c2:
        st.metric("Top Revenue Brand", top_brand["brand"])
        st.metric(
            "Brand Revenue",
            f"₹{top_brand['Revenue']:,.0f}"
        )

    st.info(
        "CommerceIQ AI identifies the strongest product categories and brands driving overall sales revenue, helping prioritize inventory investment and merchandising strategies."
    )

st.divider()

# ======================================================
# PRODUCT DEMAND MATRIX
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Product Demand Matrix</h2>
    <p>Analyze demand intensity across product categories and brands to identify high-performing combinations.</p>
</div>
""", unsafe_allow_html=True)

matrix = sales.pivot_table(
    values="quantity",
    index="category",
    columns="brand",
    aggfunc="sum",
    fill_value=0
)

fig_matrix = px.imshow(
    matrix,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_matrix.update_layout(
    title="Category vs Brand Demand Matrix",
    height=500,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=20)
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig_matrix, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# ABC PRODUCT ANALYSIS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>ABC Product Classification</h2>
    <p>Classify products based on cumulative revenue contribution for inventory prioritization.</p>
</div>
""", unsafe_allow_html=True)

abc = (
    sales.groupby("title")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

abc["Cumulative %"] = (
    abc["Revenue"].cumsum() / abc["Revenue"].sum() * 100
)

abc["Class"] = abc["Cumulative %"].apply(
    lambda x: "A" if x <= 80 else "B" if x <= 95 else "C"
)

left, right = st.columns([1.3, 0.7])

# ABC Scatter

fig_abc = px.scatter(
    abc,
    x="Cumulative %",
    y="Revenue",
    color="Class",
    hover_name="title",
    color_discrete_map={
        "A": "#10B981",
        "B": "#F59E0B",
        "C": "#EF4444"
    },
    template="plotly_dark"
)

fig_abc.update_layout(
    title="ABC Inventory Classification",
    height=500,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=20)
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_abc, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ABC Summary Card

class_summary = abc["Class"].value_counts()

with right:
    with st.container(border=True):

        st.subheader("📊 ABC Summary")

        st.metric("Class A Products", int(class_summary.get("A", 0)))
        st.metric("Class B Products", int(class_summary.get("B", 0)))
        st.metric("Class C Products", int(class_summary.get("C", 0)))

        st.info(
            "Class A products generate nearly 80% of total revenue and require the highest inventory priority."
        )

st.divider()

# ======================================================
# SMART REORDER RECOMMENDATIONS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Smart Reorder Recommendations</h2>
    <p>AI-driven inventory recommendations for low-stock products requiring replenishment.</p>
</div>
""", unsafe_allow_html=True)

recommend = products[products["stock"] < 20].copy()

recommend["Recommended Stock"] = recommend["stock"] + 50
recommend["Priority"] = recommend["stock"].apply(
    lambda x: "🔴 High" if x < 5 else "🟡 Medium"
)

with st.container(border=True):

    st.subheader("📦 Inventory Replenishment Table")

    st.dataframe(
        recommend[
            [
                "title",
                "category",
                "brand",
                "stock",
                "Recommended Stock",
                "Priority",
            ]
        ],
        use_container_width=True,
        height=400,
    )

    st.info(
        "CommerceIQ AI flags products with critical stock levels and recommends replenishment quantities to reduce stock-out risk."
    )

st.divider()

# ======================================================
# PRODUCT MASTER ANALYTICS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Product Master Analytics</h2>
    <p>Complete product-wise revenue, units sold and average selling price overview.</p>
</div>
""", unsafe_allow_html=True)

master = (
    sales.groupby(
        ["product_id", "title", "category", "brand"]
    )
    .agg(
        Revenue=("Revenue", "sum"),
        Units=("quantity", "sum"),
        Avg_Price=("unit_price", "mean"),
    )
    .reset_index()
)

with st.container(border=True):

    st.subheader("📊 Product Performance Table")

    st.dataframe(
        master.sort_values("Revenue", ascending=False),
        use_container_width=True,
        height=450,
    )

st.divider()

# ======================================================
# PRODUCT EXECUTIVE SUMMARY
# ======================================================

top_product = master.sort_values("Revenue", ascending=False).iloc[0]

with st.container(border=True):

    st.subheader("🏆 Product Executive Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Top Revenue Product", top_product["title"])
        st.metric("Revenue Generated", f"₹{top_product['Revenue']:,.0f}")
        st.metric("Units Sold", int(top_product["Units"]))

    with c2:
        st.metric("Inventory Value", f"₹{inventory_value:,.0f}")
        st.metric("Categories", categories)
        st.metric("Brands", brands)

    st.success(
        "CommerceIQ AI continuously tracks product demand, inventory turnover, revenue contribution and replenishment priorities for executive inventory planning."
    )

st.divider()

# ======================================================
# EXPORT PRODUCT REPORT
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Export Product Analytics Report</h2>
    <p>Download a complete product intelligence report for offline analysis and executive reporting.</p>
</div>
""", unsafe_allow_html=True)

csv = master.to_csv(index=False)

with st.container(border=True):

    st.subheader("⬇️ Download Analytics Report")

    st.download_button(
        label="Download Product Analytics Report (CSV)",
        data=csv,
        file_name="CommerceIQ_Product_Report.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        "The exported report includes revenue, units sold, average selling price, category and brand performance for every product."
    )

st.divider()

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-premium">
    <h3>CommerceIQ AI Executive Intelligence</h3>
    <p>
        Powered by AI • Real-Time Product Analytics • Inventory Intelligence • Executive Decision Support
    </p>
</div>
""", unsafe_allow_html=True)