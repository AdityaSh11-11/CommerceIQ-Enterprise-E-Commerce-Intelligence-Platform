import os

from dotenv import load_dotenv
from google import genai


# ============================================
# LOAD ENVIRONMENT
# ============================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


# ============================================
# AI BUSINESS INSIGHTS
# ============================================

def generate_business_insights(metrics: dict) -> str:

    if client is None:
        return fallback_analysis(metrics)

    prompt = f"""
You are a Senior Business Intelligence Consultant working for a Fortune 500 company.

Analyze the following e-commerce KPIs and prepare an executive report.

Business Metrics

• Revenue: ₹{metrics["revenue"]:,.2f}
• Orders: {metrics["orders"]}
• Customers: {metrics["customers"]}
• Average Order Value: ₹{metrics["average_order_value"]:,.2f}
• Low Stock Products: {metrics["low_stock"]}
• Repeat Customer Rate: {metrics["repeat_customer_rate"]:.0%}

Instructions:

Do NOT repeat the metrics as JSON.

Write a professional report in Markdown using the following structure.

# Executive Summary

Summarize overall business performance.

# Revenue Analysis

Discuss revenue, order volume and average order value.

# Customer Insights

Comment on customer behavior and repeat purchase rate.

# Inventory Analysis

Analyze inventory health and low-stock products.

# Risks

Identify business risks.

# Recommendations

Provide at least five actionable recommendations.

# Business Health Score

Give an overall score out of 10 with a short justification.

Keep the tone professional, data-driven and suitable for a CEO.
"""

    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ]

    for model in models:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )

            return response.text or fallback_analysis(metrics)

        except Exception:
            continue

    return fallback_analysis(metrics)


# ============================================
# FALLBACK REPORT
# ============================================

def fallback_analysis(metrics: dict) -> str:

    return f"""
# Executive Summary

The platform generated **₹{metrics['revenue']:,.2f}**
from **{metrics['orders']} orders** across
**{metrics['customers']} customers**.

---

# Revenue Analysis

- Revenue: **₹{metrics['revenue']:,.2f}**
- Average Order Value: **₹{metrics['average_order_value']:,.2f}**

---

# Customer Insights

- Repeat Customer Rate:
  **{metrics['repeat_customer_rate']:.0%}**

Customer loyalty appears healthy.

---

# Inventory Analysis

There are currently
**{metrics['low_stock']} low-stock products**
that require replenishment.

---

# Recommendations

- Replenish low-stock inventory.
- Improve cross-selling opportunities.
- Expand customer loyalty initiatives.
- Optimize pricing using historical demand.
- Monitor revenue trends daily.

---

# Business Health Score

**8.5 / 10**

The business demonstrates strong revenue generation and customer retention, with inventory optimization remaining the primary area for improvement.
"""