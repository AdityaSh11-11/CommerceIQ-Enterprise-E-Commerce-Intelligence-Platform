import streamlit as st
from sqlalchemy import create_engine, text
from config import DATABASE_URL

st.set_page_config(
    page_title="CommerceIQ",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

engine = create_engine(DATABASE_URL)

def database_status():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except:
        return False

status = "🟢 ONLINE" if database_status() else "🔴 OFFLINE"

st.markdown(f"""
<div class="hero-home">

<div class="hero-chip">
AI POWERED BUSINESS INTELLIGENCE PLATFORM
</div>

<h1>🛒 CommerceIQ</h1>

<h2>Enterprise E-Commerce Intelligence Platform</h2>

<p>
Transforming millions of e-commerce transactions into real-time dashboards,
predictive intelligence, AI-powered recommendations and executive decision support.
</p>

<div class="hero-buttons">
    <span>Executive Analytics</span>
    <span>AI Insights</span>
    <span>Live Monitoring</span>
</div>

</div>
""", unsafe_allow_html=True)


st.markdown("<h2 class='center-title'>Core Platform Capabilities</h2>", unsafe_allow_html=True)

features = [
    ("Executive Analytics",
     "Interactive KPIs, revenue monitoring, customer intelligence and executive dashboards."),

    ("Live Operations Center",
     "Real-time transaction streaming, operational alerts and automated order monitoring."),

    ("AI Decision Intelligence",
     "LLM powered business reports, recommendations and executive summaries."),

    ("Machine Learning Forecasting",
     "Demand forecasting, revenue prediction and inventory planning."),

    ("Customer Intelligence",
     "Retention analysis, customer lifetime value and segmentation."),

    ("Inventory Intelligence",
     "Stock health monitoring, reorder recommendations and inventory valuation.")
]

cols = st.columns(3)

for i, feature in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{feature[0]}</h3>
            <p>{feature[1]}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="cta-section">

<h2>Enterprise Analytics for Modern Commerce</h2>

<p>
CommerceIQ combines Business Intelligence, Machine Learning and Generative AI into one unified decision platform.
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer-premium">

<h2>CommerceIQ</h2>

<p>
Enterprise E-Commerce Intelligence Platform powered by Artificial Intelligence & Machine Learning.
</p>

<div class="footer-links">
<span>Executive Dashboards</span>
<span>AI Business Intelligence</span>
<span>Live Operations Center</span>
<span>Predictive Analytics</span>
</div>

<hr>

<p class="copyright">
© 2026 CommerceIQ • Designed & Developed by Aditya Sharma
</p>

</div>
""", unsafe_allow_html=True)
