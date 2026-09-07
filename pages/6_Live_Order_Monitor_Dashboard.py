import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy import create_engine
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

import subprocess
import os
import signal

from config import DATABASE_URL

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Live Operations Center",
    page_icon="⚡",
    layout="wide"
)

with open("dashboard_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

# ======================================================
# AUTO REFRESH (Every 2 Seconds)
# ======================================================

st_autorefresh(interval=2000, key="live_refresh")

# ======================================================
# LOAD LIVE ORDERS
# ======================================================

@st.cache_data(ttl=2)
def load_orders():

    orders = pd.read_sql(
        "SELECT * FROM orders ORDER BY order_date DESC",
        engine
    )

    orders["order_date"] = pd.to_datetime(orders["order_date"])

    return orders


orders = load_orders()

# ======================================================
# HERO SECTION (HTML SAFE)
# ======================================================

with st.container(border=True):

    st.caption("COMMERCEIQ LIVE OPERATIONS CENTER")

    st.title("⚡ Live Operations Command Center")

    st.write(
        "Monitor incoming transactions, payment flow, operational health, "
        "order velocity and live business activity in real time."
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
# LIVE TRANSACTION ENGINE CONTROL
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Transaction Engine</h2>
    <p>Start or stop the CommerceIQ live transaction simulator and monitor operational activity in real time.</p>
</div>
""", unsafe_allow_html=True)

if "engine_pid" not in st.session_state:
    st.session_state.engine_pid = None

left, right = st.columns(2)

# ---------- START ENGINE ----------

with left:

    if st.button(
        "🟢 Start Live Orders Engine",
        use_container_width=True
    ):

        if st.session_state.engine_pid is None:

            process = subprocess.Popen(
                ["python", "transaction_engine.py"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )

            st.session_state.engine_pid = process.pid

            st.success(
                f"Live Transaction Engine Started (PID: {process.pid})"
            )

        else:
            st.info("Live Engine is already running.")

# ---------- STOP ENGINE ----------

with right:

    if st.button(
        "🔴 Stop Live Orders Engine",
        use_container_width=True
    ):

        pid = st.session_state.engine_pid

        if pid:

            try:
                os.kill(pid, signal.SIGTERM)

                st.session_state.engine_pid = None

                st.success("Live Transaction Engine Stopped Successfully.")

            except Exception as e:
                st.error(f"Unable to stop engine: {e}")

        else:
            st.warning("Live Engine is not running.")

# ---------- ENGINE STATUS CARD ----------

with st.container(border=True):

    st.subheader("⚙️ Engine Status")

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        st.metric(
            "Engine Status",
            "Running" if st.session_state.engine_pid else "Stopped"
        )

    with status_col2:
        st.metric(
            "Process ID",
            st.session_state.engine_pid or "-"
        )

st.divider()

# ======================================================
# LIVE KPI CALCULATIONS
# ======================================================

revenue = orders["net_amount"].sum()

total_orders = len(orders)

today_orders = orders[
    orders["order_date"].dt.date == datetime.now().date()
]

orders_per_minute = (
    len(today_orders)
    /
    max(datetime.now().hour * 60 + datetime.now().minute, 1)
)

avg_order = revenue / total_orders if total_orders else 0

cancelled = len(
    orders[orders["status"] == "Cancelled"]
)

processing = len(
    orders[orders["status"] == "Processing"]
)

success_rate = (
    100 - cancelled / total_orders * 100
    if total_orders else 0
)

# ======================================================
# LIVE BUSINESS SNAPSHOT
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Business Snapshot</h2>
    <p>Real-time operational KPIs updating automatically every 2 seconds.</p>
</div>
""", unsafe_allow_html=True)

# ---------- KPI ROW 1 ----------

row1 = st.columns(4)

with row1[0]:
    st.metric("📦 Total Orders", f"{total_orders:,}")

with row1[1]:
    st.metric("💰 Revenue", f"₹{revenue:,.0f}")

with row1[2]:
    st.metric("🕒 Today's Orders", len(today_orders))

with row1[3]:
    st.metric("⚡ Orders / Minute", f"{orders_per_minute:.2f}")

# ---------- KPI ROW 2 ----------

row2 = st.columns(4)

with row2[0]:
    st.metric("🛒 Average Order Value", f"₹{avg_order:,.0f}")

with row2[1]:
    st.metric("✅ Success Rate", f"{success_rate:.1f}%")

with row2[2]:
    st.metric("🚚 Processing Orders", processing)

with row2[3]:
    st.metric("❌ Cancelled Orders", cancelled)

st.divider()

# ======================================================
# LIVE OPERATIONS SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📊 Operations Summary")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric("Revenue Today", f"₹{today_orders['net_amount'].sum():,.0f}")

    with s2:
        st.metric("Live Transactions", len(today_orders))

    with s3:
        st.metric("Operational Health", f"{success_rate:.1f}%")

    st.info(
        "CommerceIQ AI continuously monitors transaction flow, operational health, payment success rate and order velocity in real time."
    )

st.divider()


# ======================================================
# OPERATIONAL STATUS CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Operational Status Center</h2>
    <p>Monitor order status distribution and overall operational health in real time.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2)

# ------------------------------------------------------
# ORDER STATUS DISTRIBUTION
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
    hole=0.60,
    color="status",
    color_discrete_map={
        "Delivered": "#10B981",
        "Processing": "#3B82F6",
        "Pending": "#F59E0B",
        "Cancelled": "#EF4444",
        "Shipped": "#22D3EE"
    },
    template="plotly_dark"
)

fig_status.update_layout(
    title="Live Order Status Distribution",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    legend=dict(
        orientation="h",
        y=-0.15
    ),
    margin=dict(l=10, r=10, t=60, b=20)
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_status, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# OPERATIONAL HEALTH SCORE
# ------------------------------------------------------

health_score = round(success_rate)

fig_health = go.Figure(go.Indicator(
    mode="gauge+number",
    value=health_score,
    title={"text": "Operational Health Score"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "#22D3EE"},
        "steps": [
            {"range": [0, 50], "color": "#7F1D1D"},
            {"range": [50, 75], "color": "#92400E"},
            {"range": [75, 100], "color": "#064E3B"}
        ]
    }
))

fig_health.update_layout(
    template="plotly_dark",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=20)
)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_health, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# LIVE OPERATIONS SUMMARY
# ======================================================

delivered = len(orders[orders["status"] == "Delivered"])
pending = len(orders[orders["status"] == "Pending"])

with st.container(border=True):

    st.subheader("⚙️ Live Operations Summary")

    s1, s2 = st.columns(2)

    with s1:
        st.metric("Delivered Orders", delivered)
        st.metric("Processing Orders", processing)

    with s2:
        st.metric("Pending Orders", pending)
        st.metric("Cancelled Orders", cancelled)

    st.info(
        "CommerceIQ AI continuously monitors fulfilment rate, order pipeline health, cancellations and delivery performance in real time."
    )

st.divider()

# ======================================================
# REVENUE VELOCITY CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Revenue Velocity Center</h2>
    <p>Monitor hourly revenue generation and payment method activity across live business operations.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Hourly Revenue Data
# ------------------------------------------------------

hourly = (
    orders.groupby(orders["order_date"].dt.hour)["net_amount"]
    .sum()
    .reset_index()
)

hourly.columns = ["Hour", "Revenue"]

payment = (
    orders.groupby("payment_method")
    .size()
    .reset_index(name="Orders")
)

left, right = st.columns(2)

# ------------------------------------------------------
# Hourly Revenue Area Chart
# ------------------------------------------------------

fig_hourly = px.area(
    hourly,
    x="Hour",
    y="Revenue",
    template="plotly_dark"
)

fig_hourly.update_traces(
    line=dict(color="#38BDF8", width=3),
    fillcolor="rgba(56,189,248,0.20)"
)

fig_hourly.update_layout(
    title="Hourly Revenue Flow",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=60, b=20)
)

with left:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_hourly, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------
# Payment Distribution
# ------------------------------------------------------

fig_payment = px.bar(
    payment,
    x="payment_method",
    y="Orders",
    color="Orders",
    color_continuous_scale="Blues",
    template="plotly_dark"
)

fig_payment.update_layout(
    title="Payment Method Distribution",
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,.95)",
    font=dict(color="#F8FAFC"),
    coloraxis_showscale=False,
    margin=dict(l=10, r=10, t=60, b=20)
)

with right:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_payment, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# PAYMENT INTELLIGENCE SUMMARY
# ======================================================

top_payment = payment.sort_values("Orders", ascending=False).iloc[0]

peak_hour = hourly.sort_values("Revenue", ascending=False).iloc[0]

with st.container(border=True):

    st.subheader("💳 Payment Intelligence Summary")

    s1, s2 = st.columns(2)

    with s1:
        st.metric(
            "Top Payment Method",
            top_payment["payment_method"]
        )

        st.metric(
            "Transactions",
            int(top_payment["Orders"])
        )

    with s2:
        st.metric(
            "Peak Revenue Hour",
            f"{int(peak_hour['Hour']):02d}:00"
        )

        st.metric(
            "Revenue Generated",
            f"₹{peak_hour['Revenue']:,.0f}"
        )

    st.info(
        "CommerceIQ AI tracks customer payment preferences and identifies peak revenue hours for marketing, staffing and operational planning."
    )

st.divider()

# ======================================================
# LIVE REVENUE PERFORMANCE SUMMARY
# ======================================================

highest_hour = hourly.loc[hourly["Revenue"].idxmax()]
lowest_hour = hourly.loc[hourly["Revenue"].idxmin()]

with st.container(border=True):

    st.subheader("📈 Revenue Performance Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Peak Hour Revenue",
            f"₹{highest_hour['Revenue']:,.0f}"
        )

    with c2:
        st.metric(
            "Lowest Hour Revenue",
            f"₹{lowest_hour['Revenue']:,.0f}"
        )

    with c3:
        st.metric(
            "Average Revenue / Hour",
            f"₹{hourly['Revenue'].mean():,.0f}"
        )

    st.success(
        "Hourly revenue velocity helps CommerceIQ AI identify high-demand business windows and optimize live operational capacity."
    )

st.divider()

# ======================================================
# LIVE ORDER TIMELINE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Order Timeline</h2>
    <p>Track incoming orders, revenue spikes and live transaction activity in real time.</p>
</div>
""", unsafe_allow_html=True)

timeline = (
    orders.sort_values("order_date")
    .tail(150)
)

fig_timeline = px.scatter(
    timeline,
    x="order_date",
    y="net_amount",
    color="status",
    size="net_amount",
    hover_data=[
        "order_id",
        "customer_id",
        "payment_method"
    ],
    color_discrete_map={
        "Delivered": "#10B981",
        "Processing": "#3B82F6",
        "Pending": "#F59E0B",
        "Cancelled": "#EF4444",
        "Shipped": "#22D3EE"
    },
    template="plotly_dark"
)

fig_timeline.update_layout(
    title="Incoming Live Orders Timeline",
    height=520,
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
st.plotly_chart(fig_timeline, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ======================================================
# LIVE TRANSACTION SUMMARY
# ======================================================

latest_order = orders.iloc[0]

with st.container(border=True):

    st.subheader("🛰️ Live Transaction Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Latest Order ID",
            latest_order["order_id"]
        )

    with c2:
        st.metric(
            "Latest Order Value",
            f"₹{latest_order['net_amount']:,.0f}"
        )

    with c3:
        st.metric(
            "Latest Status",
            latest_order["status"]
        )

    st.info(
        "CommerceIQ AI refreshes this operational feed automatically every 2 seconds to provide near real-time transaction visibility."
    )

st.divider()

# ======================================================
# LIVE ORDER STATUS ACTIVITY
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Order Activity Feed</h2>
    <p>Monitor the latest operational events and customer transactions as they arrive.</p>
</div>
""", unsafe_allow_html=True)

activity = (
    orders.sort_values("order_date", ascending=False)
    .head(12)
)

for _, row in activity.iterrows():

    with st.container(border=True):

        left, right = st.columns([3,1])

        with left:
            st.markdown(
                f"**Order #{row['order_id']}** • Customer **{row['customer_id']}**"
            )
            st.caption(
                row["order_date"].strftime("%d %b %Y • %I:%M:%S %p")
            )

        with right:
            st.metric(
                row["status"],
                f"₹{row['net_amount']:,.0f}"
            )

st.divider()

# ======================================================
# AI OPERATIONS ALERT CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>AI Operations Alert Center</h2>
    <p>CommerceIQ AI continuously monitors transaction activity and operational health to generate live business alerts.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# AI Alert Cards
# ------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.subheader("⚡ Live Transaction Activity")

        if orders_per_minute > 3:
            st.success("High order velocity detected. Transaction flow is above normal levels.")

        elif orders_per_minute > 1:
            st.info("Healthy transaction activity detected across the platform.")

        else:
            st.warning("Transaction activity is currently below the normal operating level.")

    with st.container(border=True):

        st.subheader("🚚 Order Processing Health")

        if processing > 20:
            st.warning(f"{processing} orders are currently in processing state.")

        else:
            st.success("Order processing pipeline is operating normally.")

with col2:

    with st.container(border=True):

        st.subheader("❌ Cancellation Monitoring")

        cancellation_rate = (
            cancelled / total_orders * 100
            if total_orders else 0
        )

        if cancellation_rate > 10:
            st.error(
                f"Cancellation rate is {cancellation_rate:.1f}%. Immediate operational review recommended."
            )

        else:
            st.success(
                f"Cancellation rate is under control ({cancellation_rate:.1f}%)."
            )

    with st.container(border=True):

        st.subheader("🟢 Operational Health")

        if success_rate >= 95:
            st.success("Operational success rate is excellent.")

        elif success_rate >= 85:
            st.info("Operational success rate is healthy.")

        else:
            st.warning("Operational success rate requires attention.")

st.divider()

# ======================================================
# LIVE ALERT SUMMARY
# ======================================================

with st.container(border=True):

    st.subheader("📊 AI Operations Summary")

    a1, a2, a3 = st.columns(3)

    with a1:
        st.metric("Success Rate", f"{success_rate:.1f}%")

    with a2:
        st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")

    with a3:
        st.metric("Orders Per Minute", f"{orders_per_minute:.2f}")

    st.info(
        "CommerceIQ AI evaluates operational health using live transaction velocity, payment success rate and fulfilment status."
    )

st.divider()

# ======================================================
# LIVE INCOMING ORDERS TABLE
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Live Incoming Orders</h2>
    <p>Monitor the latest customer orders as they arrive in the CommerceIQ transaction engine.</p>
</div>
""", unsafe_allow_html=True)

recent_orders = (
    orders.sort_values("order_date", ascending=False)
    .head(30)
)

with st.container(border=True):

    st.subheader("📦 Recent Live Orders")

    st.dataframe(
        recent_orders[
            [
                "order_id",
                "customer_id",
                "payment_method",
                "status",
                "net_amount",
                "order_date"
            ]
        ],
        use_container_width=True,
        height=500
    )

st.divider()

# ======================================================
# LIVE ORDER INSIGHTS
# ======================================================

latest = recent_orders.iloc[0]

with st.container(border=True):

    st.subheader("📋 Latest Transaction Insight")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Latest Order", latest["order_id"])
        st.metric("Customer ID", latest["customer_id"])

    with c2:
        st.metric("Payment Method", latest["payment_method"])
        st.metric("Order Value", f"₹{latest['net_amount']:,.0f}")

    st.caption(
        f"Last transaction received on {latest['order_date'].strftime('%d %b %Y • %I:%M:%S %p')}"
    )

st.divider()

# ======================================================
# EXPORT LIVE ORDERS CENTER
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>Export Live Operations Report</h2>
    <p>Download the latest live transactions and operational data for reporting, auditing and Power BI analysis.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# Prepare Export File
# ------------------------------------------------------

live_orders_csv = recent_orders.to_csv(index=False)

# ------------------------------------------------------
# Export Summary Card
# ------------------------------------------------------

with st.container(border=True):

    st.subheader("📄 Live Operations Report Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Live Orders Included", len(recent_orders))

    with c2:
        st.metric("Export Format", "CSV")

    with c3:
        st.metric(
            "Generated At",
            datetime.now().strftime("%H:%M:%S")
        )

    st.success(
        "CommerceIQ exports the latest operational transactions in a Power BI and Excel compatible CSV format."
    )

st.divider()

# ======================================================
# DOWNLOAD BUTTON
# ======================================================

with st.container(border=True):

    st.subheader("⬇️ Download Live Orders Report")

    st.write(
        "The report includes order ID, customer ID, payment method, status, revenue amount and timestamp for the latest live transactions."
    )

    st.download_button(
        label="📥 Download CommerceIQ Live Orders CSV",
        data=live_orders_csv,
        file_name="CommerceIQ_Live_Orders_Report.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

# ======================================================
# LIVE ENGINE STATUS PANEL
# ======================================================

with st.container(border=True):

    st.subheader("⚙️ Live Engine Monitoring")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Engine Status",
            "🟢 Running" if st.session_state.engine_pid else "🔴 Stopped"
        )

    with s2:
        st.metric(
            "Refresh Interval",
            "2 Seconds"
        )

    with s3:
        st.metric(
            "Current Timestamp",
            datetime.now().strftime("%d %b %Y")
        )

    st.info(
        "CommerceIQ Live Operations Center refreshes automatically every 2 seconds to provide near real-time operational visibility."
    )

st.divider()

# ======================================================
# LIVE OPERATIONS INSIGHTS
# ======================================================

st.markdown("""
<div class="section-header">
    <h2>CommerceIQ Live Intelligence</h2>
    <p>Real-time operational monitoring powered by CommerceIQ AI Business Intelligence Engine.</p>
</div>
""", unsafe_allow_html=True)

i1, i2 = st.columns(2)

with i1:
    with st.container(border=True):
        st.markdown("### 🚚 Order Fulfilment")
        st.write(
            "- Track live order processing.\n"
            "- Monitor fulfilment pipeline.\n"
            "- Detect operational bottlenecks."
        )

with i2:
    with st.container(border=True):
        st.markdown("### 💳 Payment Monitoring")
        st.write(
            "- Monitor payment methods in real time.\n"
            "- Analyze transaction velocity.\n"
            "- Identify operational anomalies instantly."
        )

st.divider()

# ======================================================
# FOOTER
# ======================================================

st.markdown("""
<div class="footer-premium">

## CommerceIQ Live Operations Intelligence

Real-Time Transactions • Operational Health • Payment Monitoring • AI Command Center

<div class="footer-links">
    <span>Live Orders</span>
    <span>Revenue Velocity</span>
    <span>Operational Alerts</span>
    <span>Command Center</span>
</div>

<hr>

<p class="copyright">
© 2026 CommerceIQ • Live Operations Command Center
</p>

</div>
""", unsafe_allow_html=True)