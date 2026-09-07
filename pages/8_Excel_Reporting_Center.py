import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

from config import DATABASE_URL
from excel_reports import generate_excel_report

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Excel Reporting Center",
    page_icon="📊",
    layout="wide"
)

with open("dashboard_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data(ttl=30)
def load_data():

    orders = pd.read_sql("SELECT * FROM orders", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    return orders, customers, products, order_items


orders, customers, products, order_items = load_data()

# ======================================================
# KPI CALCULATIONS
# ======================================================

revenue = orders["net_amount"].sum()
orders_count = len(orders)
customers_count = len(customers)

profit = revenue - orders["tax"].sum()

aov = revenue / orders_count if orders_count else 0

products_sold = order_items["quantity"].sum()

low_stock = int((products["stock"] < 20).sum())

inventory_value = (products["price"] * products["stock"]).sum()

# ======================================================
# HERO SECTION
# ======================================================

# ======================================================
# HERO SECTION
# ======================================================
st.html("""
<div class="hero-small">
    <div class="hero-chip">COMMERCEIQ EXCEL REPORTING SUITE</div>

    <h1>Excel Reporting Center</h1>

    <p>
        Generate enterprise-ready Excel dashboards, Pivot Tables,
        financial reports, inventory workbooks and executive business reports
        directly from CommerceIQ analytics.
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
# KPI SECTION
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Excel Executive Snapshot</h2>
    <p>Real-time CommerceIQ business KPIs ready for enterprise Excel reporting.</p>
</div>
""", unsafe_allow_html=True)

# ---------- KPI Row 1 ----------

row1 = st.columns(4)

with row1[0]:
    st.metric("💰 Revenue", f"₹{revenue:,.0f}")

with row1[1]:
    st.metric("📦 Orders", f"{orders_count:,}")

with row1[2]:
    st.metric("👥 Customers", f"{customers_count:,}")

with row1[3]:
    st.metric("📈 Profit", f"₹{profit:,.0f}")

# ---------- KPI Row 2 ----------

row2 = st.columns(4)

with row2[0]:
    st.metric("🛒 Avg Order Value", f"₹{aov:,.0f}")

with row2[1]:
    st.metric("📦 Products Sold", int(products_sold))

with row2[2]:
    st.metric("⚠️ Low Stock Products", low_stock)

with row2[3]:
    st.metric("🏬 Inventory Value", f"₹{inventory_value:,.0f}")

st.divider()

# ======================================================
# REPORTING SNAPSHOT
# ======================================================

with st.container(border=True):

    st.subheader("📊 Reporting Snapshot")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Available Reports", 6)

    with c2:
        st.metric("Excel Sheets Supported", 12)

    with c3:
        st.metric("Export Format", "XLSX")

    st.info(
        "CommerceIQ generates executive Excel workbooks with KPIs, Pivot Tables, conditional formatting, inventory intelligence and financial summaries."
    )

st.divider()


# ======================================================
# ENTERPRISE REPORT GENERATOR
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Generate Enterprise Excel Reports</h2>
    <p>Select a reporting template and generate an executive-ready Excel workbook instantly.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Report Template Selection
# ------------------------------------------------------

report_type = st.selectbox(
    "📑 Select Excel Report Template",
    [
        "Executive Dashboard Report",
        "Sales Analytics Report",
        "Customer Analytics Report",
        "Inventory Analytics Report",
        "Financial Summary Report",
        "Complete CommerceIQ Workbook"
    ],
    index=0
)

st.divider()

# ======================================================
# REPORT INFORMATION CARD
# ======================================================

with st.container(border=True):

    st.subheader("📊 Selected Report Overview")

    st.markdown(f"### **{report_type}**")

    report_descriptions = {
        "Executive Dashboard Report":
            "Executive KPI dashboard with revenue, orders, customers, profit and business summary.",

        "Sales Analytics Report":
            "Sales trends, top products, category performance, hourly sales and revenue analytics.",

        "Customer Analytics Report":
            "Customer segmentation, repeat customers, lifetime value, geography and customer intelligence.",

        "Inventory Analytics Report":
            "Inventory health, stock analysis, ABC classification, reorder recommendations and warehouse insights.",

        "Financial Summary Report":
            "Financial transactions, discounts, taxes, shipping, net revenue and profitability summary.",

        "Complete CommerceIQ Workbook":
            "A complete enterprise workbook containing all CommerceIQ dashboards, pivot tables, KPIs and analytics sheets."
    }

    st.write(report_descriptions[report_type])

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Sheets Included", "8–12")

    with c2:
        st.metric("Pivot Tables", "Included")

    with c3:
        st.metric("Conditional Formatting", "Enabled")

    st.success(
        "Every workbook is professionally formatted with KPI summaries, filters, tables, charts and executive-ready layouts."
    )

st.divider()

# ======================================================
# REPORT FEATURES
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Workbook Features</h2>
    <p>Every CommerceIQ Excel workbook is designed for business executives, analysts and Power BI users.</p>
</div>
""", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

with f1:
    with st.container(border=True):
        st.markdown("### 📊")
        st.markdown("**Executive KPI Dashboard**")
        st.caption("Revenue, Orders, Profit, Customers")

with f2:
    with st.container(border=True):
        st.markdown("### 📈")
        st.markdown("**Pivot Tables & Charts**")
        st.caption("Dynamic Excel analytics")

with f3:
    with st.container(border=True):
        st.markdown("### 🎨")
        st.markdown("**Conditional Formatting**")
        st.caption("Automatic business highlighting")

with f4:
    with st.container(border=True):
        st.markdown("### 📁")
        st.markdown("**Multi-Sheet Workbook**")
        st.caption("Enterprise reporting structure")

st.divider()

# ======================================================
# LIVE EXCEL REPORT PREVIEW CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Excel Report Preview</h2>
    <p>Preview the first records of the selected report before generating the enterprise Excel workbook.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Report Preview Data
# ------------------------------------------------------

if report_type == "Executive Dashboard Report":

    preview = orders[
        ["order_id","customer_id","status","payment_method","net_amount"]
    ].head(12)

elif report_type == "Sales Analytics Report":

    preview = (
        order_items
        .merge(products, on="product_id")
        [["title","category","brand","quantity","unit_price"]]
        .head(12)
    )

elif report_type == "Customer Analytics Report":

    preview = customers.head(12)

elif report_type == "Inventory Analytics Report":

    preview = products.head(12)

elif report_type == "Financial Summary Report":

    preview = orders[
        ["order_id","total_amount","discount","tax","shipping","net_amount"]
    ].head(12)

else:

    preview = orders.head(12)

# ------------------------------------------------------
# Preview Summary Cards
# ------------------------------------------------------

rows = len(preview)
columns = len(preview.columns)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Preview Rows", rows)

with col2:
    st.metric("Columns Included", columns)

with col3:
    st.metric("Workbook Status", "Ready")

st.divider()

# ------------------------------------------------------
# Live Preview Table
# ------------------------------------------------------

with st.container(border=True):

    st.subheader("📄 Report Data Preview")

    st.dataframe(
        preview,
        use_container_width=True,
        height=420
    )

st.divider()

# ======================================================
# REPORT PREVIEW INSIGHTS
# ======================================================

with st.container(border=True):

    st.subheader("📊 Preview Insights")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Selected Template", report_type)

    with c2:
        st.metric("Last Updated", datetime.now().strftime("%d %b %Y"))

    st.info(
        "The preview displays the first records that will be included in the generated Excel workbook. The exported workbook contains formatted tables, KPI summaries and business-ready sheets."
    )

st.divider()

# ======================================================
# GENERATE ENTERPRISE EXCEL WORKBOOK
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Generate Enterprise Excel Workbook</h2>
    <p>Create a professionally formatted multi-sheet Excel workbook for executives, analysts and Power BI reporting.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Workbook Summary
# ------------------------------------------------------

with st.container(border=True):

    st.subheader("📁 Workbook Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Selected Template", report_type)

    with c2:
        st.metric("Output Format", "XLSX")

    with c3:
        st.metric("Workbook Status", "Ready")

    st.info(
        "The generated workbook includes formatted sheets, KPI dashboards, pivot tables, charts and executive-ready business reports."
    )

st.divider()

# ------------------------------------------------------
# Generate Button
# ------------------------------------------------------

generate = st.button(
    "🚀 Generate Excel Workbook",
    use_container_width=True
)

# ------------------------------------------------------
# Workbook Generation
# ------------------------------------------------------

if generate:

    with st.spinner("Generating Enterprise Excel Workbook..."):

        file_path = generate_excel_report(
            report_type,
            orders,
            customers,
            products,
            order_items
        )

    st.success("✅ Enterprise Excel Workbook Generated Successfully!")

    st.balloons()

    with open(file_path, "rb") as excel_file:

        st.download_button(
            label="📥 Download CommerceIQ Excel Workbook",
            data=excel_file,
            file_name=file_path.split("/")[-1],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.divider()

# ======================================================
# EXPORT FEATURES
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>What's Included in Your Workbook?</h2>
    <p>Every CommerceIQ workbook follows enterprise reporting standards.</p>
</div>
""", unsafe_allow_html=True)

f1, f2 = st.columns(2)
f3, f4 = st.columns(2)

with f1:
    with st.container(border=True):
        st.markdown("### 📊 Executive Dashboard")
        st.caption("Revenue, Profit, Orders, Customers & KPI Summary.")

with f2:
    with st.container(border=True):
        st.markdown("### 📈 Pivot Tables & Charts")
        st.caption("Interactive Excel Pivot Tables and business visualizations.")

with f3:
    with st.container(border=True):
        st.markdown("### 📦 Inventory & Financial Sheets")
        st.caption("Inventory health, stock analysis and financial summaries.")

with f4:
    with st.container(border=True):
        st.markdown("### 🎨 Executive Formatting")
        st.caption("Professional colors, filters, conditional formatting and business layouts.")

st.divider()

# ======================================================
# REPORT EXPORT STATUS
# ======================================================

with st.container(border=True):

    st.subheader("📋 Export Status")

    st.metric(
        "Last Refreshed",
        datetime.now().strftime("%d %b %Y • %I:%M %p")
    )

    st.success(
        "CommerceIQ exports business-ready Excel workbooks compatible with Microsoft Excel, Google Sheets and Power BI."
    )

st.divider()

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-premium">

## CommerceIQ Excel Intelligence Platform

Enterprise Excel Reporting • Pivot Analytics • Financial Reporting • Power BI Ready

<div class="footer-links">
    <span>Executive Dashboards</span>
    <span>Sales Analytics</span>
    <span>Customer Reports</span>
    <span>Inventory Intelligence</span>
</div>

<hr>

<p class="copyright">
© 2026 CommerceIQ • Enterprise Excel Reporting Center
</p>

</div>
""", unsafe_allow_html=True)