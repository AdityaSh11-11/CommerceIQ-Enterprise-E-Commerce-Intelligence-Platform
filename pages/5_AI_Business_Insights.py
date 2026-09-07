import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

from config import DATABASE_URL
from ai import generate_business_insights

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="AI Executive Intelligence",
    page_icon="🤖",
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

    orders = pd.read_sql("SELECT * FROM orders", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    return orders, products, customers, order_items


orders, products, customers, order_items = load_data()

# ======================================================
# BUSINESS METRICS
# ======================================================

revenue = orders["net_amount"].sum()
total_orders = len(orders)
total_customers = len(customers)

avg_order_value = (
    revenue / total_orders
    if total_orders else 0
)

products_sold = order_items["quantity"].sum()

low_stock = len(products[products["stock"] < 20])

repeat_rate = (
    orders["customer_id"]
    .value_counts()
    .gt(1)
    .mean()
)

profit = revenue - orders["tax"].sum()

inventory_value = (
    products["price"] * products["stock"]
).sum()

metrics = {
    "revenue": round(revenue, 2),
    "orders": total_orders,
    "customers": total_customers,
    "average_order_value": round(avg_order_value, 2),
    "low_stock": low_stock,
    "repeat_customer_rate": round(repeat_rate, 2),
}

# ======================================================
# BUSINESS HEALTH SCORE
# ======================================================

score = 100

if low_stock > 60:
    score -= 15

if repeat_rate < 0.50:
    score -= 15

if avg_order_value < 4000:
    score -= 10

if score >= 90:
    health = "Excellent"
elif score >= 75:
    health = "Healthy"
else:
    health = "Needs Attention"

# ======================================================
# HERO SECTION (HTML SAFE)
# ======================================================

with st.container(border=True):

    st.caption("COMMERCEIQ AI EXECUTIVE INTELLIGENCE")

    st.title("🤖 AI Executive Intelligence Center")

    st.write(
        "CommerceIQ AI analyzes real-time business performance, identifies operational risks, "
        "monitors customer behaviour, inventory health and revenue trends, and generates executive-level recommendations."
    )

st.divider()

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
# AI BUSINESS SNAPSHOT
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Business Snapshot</h2>
    <p>Real-time executive KPIs powering CommerceIQ AI decision intelligence.</p>
</div>
""", unsafe_allow_html=True)

# ---------- KPI ROW 1 ----------

row1 = st.columns(4)

with row1[0]:
    st.metric("💰 Revenue", f"₹{revenue:,.0f}")

with row1[1]:
    st.metric("📦 Orders", f"{total_orders:,}")

with row1[2]:
    st.metric("👥 Customers", f"{total_customers:,}")

with row1[3]:
    st.metric("📈 Estimated Profit", f"₹{profit:,.0f}")

# ---------- KPI ROW 2 ----------

row2 = st.columns(4)

with row2[0]:
    st.metric("🛒 Avg Order Value", f"₹{avg_order_value:,.0f}")

with row2[1]:
    st.metric("📦 Products Sold", int(products_sold))

with row2[2]:
    st.metric("❤️ Repeat Customer Rate", f"{repeat_rate:.0%}")

with row2[3]:
    st.metric("⚠️ Low Stock Products", low_stock)

st.divider()

# ======================================================
# EXECUTIVE BUSINESS SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📊 Executive Business Summary")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Inventory Capital",
            f"₹{inventory_value:,.0f}"
        )

    with s2:
        st.metric(
            "Business Health Score",
            f"{score}/100"
        )

    with s3:
        st.metric(
            "Overall Status",
            health
        )

    st.info(
        "CommerceIQ AI continuously evaluates revenue growth, customer retention, "
        "inventory health and operational efficiency to support executive business decisions."
    )

st.divider()

# ======================================================
# AI BUSINESS HEALTH MONITOR
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Business Health Monitor</h2>
    <p>CommerceIQ AI evaluates overall business health using revenue, inventory, customer retention and operational performance.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2)

# ------------------------------------------------------
# Business Health Card
# ------------------------------------------------------

with left:
    with st.container(border=True):

        st.subheader("💙 Business Health Score")

        st.metric(
            "Overall Score",
            f"{score}/100"
        )

        st.metric(
            "Current Status",
            health
        )

        if score >= 90:
            st.success("Business performance is operating at an executive level.")

        elif score >= 75:
            st.info("Business performance is healthy with minor improvement opportunities.")

        else:
            st.warning("Business requires executive attention across key KPIs.")

# ------------------------------------------------------
# AI Engine Status Card
# ------------------------------------------------------

with right:
    with st.container(border=True):

        st.subheader("🤖 AI Engine Status")

        st.metric("AI Status", "ACTIVE")

        st.metric("AI Provider", "Google Gemini")

        st.metric("Model Mode", "Executive Intelligence")

        st.success("Gemini AI Connected • Real-Time Business Analysis Enabled")

st.divider()

# ======================================================
# EXECUTIVE HEALTH SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📊 Executive Health Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Inventory Value",
            f"₹{inventory_value:,.0f}"
        )

    with c2:
        st.metric(
            "Repeat Customer Rate",
            f"{repeat_rate:.0%}"
        )

    with c3:
        st.metric(
            "Average Order Value",
            f"₹{avg_order_value:,.0f}"
        )

    st.info(
        "CommerceIQ AI continuously measures business stability using inventory health, customer loyalty, order profitability and revenue performance."
    )

st.divider()


# ======================================================
# AI RISK INTELLIGENCE CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Risk Intelligence Center</h2>
    <p>CommerceIQ AI continuously monitors inventory, customer retention, profitability and operational risks across the business.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Risk Calculations
# ------------------------------------------------------

inventory_risk = (
    "High" if low_stock > 60
    else "Medium" if low_stock > 25
    else "Low"
)

customer_risk = (
    "High" if repeat_rate < 0.50
    else "Medium" if repeat_rate < 0.70
    else "Low"
)

profit_margin = (profit / revenue * 100) if revenue else 0

profit_risk = (
    "High" if profit_margin < 20
    else "Medium" if profit_margin < 35
    else "Low"
)

order_risk = (
    "High" if avg_order_value < 4000
    else "Medium" if avg_order_value < 6000
    else "Low"
)

# ------------------------------------------------------
# Executive Risk KPI Cards
# ------------------------------------------------------

row1 = st.columns(4)

with row1[0]:
    st.metric("📦 Inventory Risk", inventory_risk)

with row1[1]:
    st.metric("❤️ Customer Retention Risk", customer_risk)

with row1[2]:
    st.metric("💹 Profitability Risk", profit_risk)

with row1[3]:
    st.metric("🛒 Order Value Risk", order_risk)

st.divider()

# ======================================================
# RISK SUMMARY CARDS
# ======================================================

left, right = st.columns(2)

with left:

    with st.container(border=True):

        st.subheader("📦 Inventory Intelligence")

        st.metric(
            "Low Stock Products",
            low_stock
        )

        st.metric(
            "Inventory Capital",
            f"₹{inventory_value:,.0f}"
        )

        if inventory_risk == "High":
            st.error("Inventory replenishment is recommended immediately.")

        elif inventory_risk == "Medium":
            st.warning("Monitor inventory levels for upcoming demand.")

        else:
            st.success("Inventory health is currently stable.")

with right:

    with st.container(border=True):

        st.subheader("👥 Customer Intelligence")

        st.metric(
            "Repeat Customer Rate",
            f"{repeat_rate:.0%}"
        )

        st.metric(
            "Average Customer Value",
            f"₹{revenue / total_customers:,.0f}"
        )

        if customer_risk == "High":
            st.error("Customer retention campaigns are recommended.")

        elif customer_risk == "Medium":
            st.warning("Retention performance is average.")

        else:
            st.success("Customer loyalty performance is healthy.")

st.divider()

# ======================================================
# EXECUTIVE RISK SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("🚨 Executive Risk Summary")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Estimated Profit Margin",
            f"{profit_margin:.1f}%"
        )

        st.metric(
            "Average Order Value",
            f"₹{avg_order_value:,.0f}"
        )

    with c2:
        st.metric(
            "Products Sold",
            int(products_sold)
        )

        st.metric(
            "Business Health Score",
            f"{score}/100"
        )

    st.info(
        "CommerceIQ AI combines inventory health, customer loyalty, profitability and revenue metrics to identify executive business risks before they impact growth."
    )

st.divider()


# ======================================================
# AI EXECUTIVE REPORT GENERATOR
# ======================================================

st.markdown("---")

st.markdown("""
<div class="section-title">
    AI Executive Report Generator
</div>
<div class="section-subtitle">
    Generate boardroom-ready business intelligence reports using CommerceIQ AI.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:

    generate = st.button(
        "Generate AI Executive Report",
        use_container_width=True
    )

with col2:

    if st.button(
        "Refresh Business Metrics",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()

if generate:

    with st.spinner(
        "CommerceIQ AI is analyzing enterprise performance..."
    ):

        report = generate_business_insights(metrics)

    st.success(
        "Executive Intelligence Report Generated Successfully"
    )

    st.markdown(f"""
    <div class="glass-card">

    <h4>Report Information</h4>

    <b>Generated:</b>
    {datetime.now().strftime("%d %B %Y • %I:%M %p")}

    <br><br>

    <b>Analysis Scope:</b>
    Revenue • Customers • Inventory • Orders • Profitability

    </div>
    """, unsafe_allow_html=True)

    st.markdown(report)

    st.download_button(
        "Download Executive Intelligence Report",
        report,
        file_name="CommerceIQ_AI_Executive_Report.md",
        mime="text/markdown",
        use_container_width=True
    )

# ======================================================
# BUSINESS METRICS SNAPSHOT
# ======================================================

st.markdown("---")

st.markdown("""
<div class="section-title">
    Business Metrics Snapshot
</div>
<div class="section-subtitle">
    Executive overview of CommerceIQ business performance and AI intelligence metrics.
</div>
""", unsafe_allow_html=True)

snapshot = pd.DataFrame({
    "Business Metric": [
        "Total Revenue",
        "Total Orders",
        "Total Customers",
        "Average Order Value",
        "Products Sold",
        "Repeat Customer Rate",
        "Low Stock Products",
        "Estimated Profit",
        "Inventory Value",
        "Business Health Score"
    ],
    "Current Value": [
        f"₹{revenue:,.2f}",
        total_orders,
        total_customers,
        f"₹{avg_order_value:,.2f}",
        int(products_sold),
        f"{repeat_rate:.0%}",
        low_stock,
        f"₹{profit:,.2f}",
        f"₹{inventory_value:,.2f}",
        f"{score}/100 ({health})"
    ]
})

with st.container(border=True):

    st.subheader("📊 Executive KPI Table")

    st.dataframe(
        snapshot,
        use_container_width=True,
        height=420
    )

st.divider()

# ======================================================
# AI EXECUTIVE SUMMARY PANEL
# ======================================================

st.markdown("""
<div class="section-title">
    AI Executive Intelligence Summary
</div>
<div class="section-subtitle">
    CommerceIQ AI executive interpretation of overall business performance.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown("### 📈 Revenue Intelligence")

        st.metric("Total Revenue", f"₹{revenue:,.0f}")
        st.metric("Estimated Profit", f"₹{profit:,.0f}")
        st.metric("Average Order Value", f"₹{avg_order_value:,.0f}")

        st.success("Revenue pipeline remains connected with CommerceIQ AI monitoring.")

with col2:

    with st.container(border=True):

        st.markdown("### 🤖 AI Business Intelligence")

        st.metric("Business Health Score", f"{score}/100")
        st.metric("Overall Status", health)
        st.metric("Repeat Customer Rate", f"{repeat_rate:.0%}")

        st.info("AI continuously evaluates customer loyalty, operational efficiency and inventory readiness.")

st.divider()

# ======================================================
# AI STRATEGIC DECISION SUMMARY
# ======================================================

st.markdown("""
<div class="section-title">
    AI Strategic Decision Summary
</div>
<div class="section-subtitle">
    Executive recommendations generated from CommerceIQ AI intelligence engine.
</div>
""", unsafe_allow_html=True)

with st.container(border=True):

    st.markdown("### 🚀 Executive Recommendations")

    st.write(
        "- Focus inventory replenishment for low-stock products before demand peaks.\n"
        "- Increase customer retention through loyalty and repeat-order campaigns.\n"
        "- Improve Average Order Value using bundles and cross-selling strategies.\n"
        "- Monitor business health score regularly through CommerceIQ AI dashboards."
    )

    st.success(
        "CommerceIQ AI transforms live operational metrics into actionable executive business intelligence."
    )

st.divider()

# ======================================================
# PREMIUM FOOTER
# ======================================================

st.markdown("""
<div class="footer-premium">

## 🤖 CommerceIQ AI Executive Intelligence Center

Real-Time Business Intelligence • AI Risk Analysis • Executive Reporting • Strategic Decision Support

<div class="footer-links">
    <span>Executive AI</span>
    <span>Business Health</span>
    <span>Risk Intelligence</span>
    <span>Gemini AI Reports</span>
</div>

<hr>

<p class="copyright">
© 2026 CommerceIQ • AI Executive Intelligence Dashboard
</p>

</div>
""", unsafe_allow_html=True)