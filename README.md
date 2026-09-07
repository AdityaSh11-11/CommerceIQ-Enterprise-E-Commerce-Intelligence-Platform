# 🚀 CommerceIQ — AI Powered Enterprise E-Commerce Analytics Platform

<p align="center">
  <b>End-to-End Business Intelligence Platform built using Python, SQL, Streamlit, SQLite & Power BI</b>
</p>

<p align="center">
  Enterprise Analytics • AI Insights • Customer Intelligence • Sales Intelligence • Data Engineering
</p>

---

## 🌟 About CommerceIQ

**CommerceIQ** is a production-style **Enterprise E-Commerce Analytics Platform** that transforms raw transactional data into actionable business intelligence.

It combines **Data Engineering, SQL Analytics, Business Intelligence, Customer Segmentation, AI-driven Insights, and Interactive Dashboards** into one centralized analytics application — similar to internal analytics tools used by companies like Amazon, Flipkart, Swiggy, Blinkit, Myntra, Meesho and Walmart.

The platform is designed to help business teams monitor sales, identify customer behavior, optimize product performance, and manage operational datasets through a secure admin portal.

---

# 🎯 Business Problems Solved

<table><table-row><table-cell width="36">📈</table-cell><table-cell><text weight=medium>Sales Intelligence</text></table-cell><table-cell>Identify revenue trends, seasonal demand, category growth and regional sales performance.</table-cell></table-row><table-row><table-cell>👥</table-cell><table-cell><text weight=medium>Customer Intelligence</text></table-cell><table-cell>Segment customers using RFM analysis, identify VIP customers and detect churn risk.</table-cell></table-row><table-row><table-cell>🛍️</table-cell><table-cell><text weight=medium>Product Intelligence</text></table-cell><table-cell>Track best-selling products, inventory health, ratings and brand performance.</table-cell></table-row><table-row><table-cell>🤖</table-cell><table-cell><text weight=medium>AI Business Insights</text></table-cell><table-cell>Automatically generate business recommendations, KPI summaries and growth opportunities.</table-cell></table-row><table-row><table-cell>⚙️</table-cell><table-cell><text weight=medium>Data Engineering</text></table-cell><table-cell>Clean, validate and upload large datasets directly into SQLite with automatic schema detection.</table-cell></table-row></table>

---

# 📊 Project Highlights

<box gap=3>
  <row align=start gap=3>
    <icon name=database color="#16A34A" size=2xl/>
    <box gap=0>
      <text weight=medium color="#16A34A">50,000+ E-Commerce Records Processed</text>
      Customers • Orders • Products • Order Items
    </box>
  </row>

  <row align=start gap=3>
    <icon name=bar-chart color="#2563EB" size=2xl/>
    <box gap=0>
      <text weight=medium color="#2563EB">Interactive Business Intelligence Dashboards</text>
      Streamlit + Plotly + Power BI
    </box>
  </row>

  <row align=start gap=3>
    <icon name=brain color="#9333EA" size=2xl/>
    <box gap=0>
      <text weight=medium color="#9333EA">AI Driven Business Insights</text>
      Automated recommendations and KPI summaries
    </box>
  </row>

  <row align=start gap=3>
    <icon name=shield-check color="#EA580C" size=2xl/>
    <box gap=0>
      <text weight=medium color="#EA580C">Enterprise Admin Panel</text>
      Smart Upload Center • Dynamic Forms • Database Management
    </box>
  </row>
</box>

---

# 🧠 Key Features

### 📈 Executive Analytics Dashboard

* Revenue, Profit & Order KPIs
* Daily / Monthly / Yearly Sales Trends
* Customer Growth Analysis
* Brand & Category Performance
* Geographic Sales Distribution
* Interactive Plotly Visualizations

---

### 👥 Customer Analytics

* Customer Lifetime Value (CLV)
* New vs Returning Customers
* Customer Purchase Frequency
* Average Order Value
* Top Spending Customers
* Customer City & Country Distribution

---

### 💎 RFM Customer Segmentation

Recency • Frequency • Monetary Analysis

Segments generated automatically:

* 🟢 Champions
* 💎 Loyal Customers
* ⭐ Potential Loyalists
* 🟡 At Risk Customers
* 🔴 Lost Customers
* 👤 New Customers

Business teams can directly identify high-value and churn-risk customers.

---

### 🛒 Product Intelligence Dashboard

* Top Selling Products
* Worst Performing Products
* Inventory Health
* Product Ratings Analysis
* Brand Revenue Contribution
* Category-wise Sales Performance

---

### 🤖 AI Insights Engine

Automatically generates:

* Top business opportunities.
* High revenue generating categories.
* Low performing products.
* Customer retention recommendations.
* Revenue leakage through discount analysis.
* Shipping cost optimization insights.

---

### 📤 Smart Data Upload Center

Enterprise-grade upload pipeline.

#### Features

* Upload **CSV / Excel**
* Automatic Table Detection
* Schema Validation
* Data Cleaning Engine
* Duplicate Detection
* Auto Column Mapping
* Bulk Upload (50,000+ records)
* Replace Existing Data
* Undo Last Upload
* Upload History

Supports automatic routing into:

* Orders
* Customers
* Products
* Order Items

---

### ✍️ Dynamic SQLite Manual Entry

Forms generated dynamically using SQLite schema.

* Auto Detect Column Types
* Date Picker
* Dropdown Foreign Keys
* Payment Method Selector
* Status Selector
* Automatic Net Amount Calculation
* Primary Key Protection

---

### 🗄️ Live Database Management

* Live Table Preview
* Global Search
* Column Filters
* Pagination
* CSV Export
* Delete by Primary Key
* Delete Order with Cascade
* Refresh Database
* Clear Selected Table
* Clear Entire Database (Schema Safe)

---

### 📊 Power BI Executive Dashboard

Professional BI dashboard created using the same SQLite database.

Includes:

* Executive KPI Cards
* Sales Performance Dashboard
* Customer Dashboard
* Product Dashboard
* Regional Sales Dashboard
* Dynamic Filters & Drill Downs

---

# 🧱 System Architecture

```text
                    ┌────────────────────────┐
                    │   CSV / Excel Upload   │
                    └──────────┬─────────────┘
                               │
                     Smart Cleaning Engine
                               │
                     Schema Validation Layer
                               │
              Automatic Table Detection (AI Logic)
                               │
          ┌──────────┬──────────┬──────────┬──────────┐
          ▼          ▼          ▼          ▼
      Customers    Orders    Products   Order Items
          │          │          │          │
          └──────────┴──────────┴──────────┘
                     SQLite Database
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
 Streamlit Dashboard   AI Insights Engine   Power BI Reports
```

---

# 📁 Project Structure

```text
CommerceIQ/
│
├── app.py
├── config.py
├── dashboard_style.css
├── requirements.txt
├── README.md
│
├── database/
│   ├── commerceiq.db
│   └── schema.sql
│
├── pages/
│   ├── Home.py
│   ├── Customer_Analytics.py
│   ├── Sales_Analytics.py
│   ├── Product_Analytics.py
│   ├── RFM_Analysis.py
│   ├── AI_Insights.py
│   ├── PowerBI_Dashboard.py
│   ├── Data_Upload_Center.py
│   └── Admin_Tools.py
│
├── datasets/
│   ├── ecommerce_orders_50000.csv
│   └── ecommerce_orders_50000.xlsx
│
├── assets/
│   ├── dashboard_preview.png
│   ├── upload_center.png
│   ├── powerbi_dashboard.png
│   └── customer_dashboard.png
│
└── notebooks/
    ├── data_cleaning.ipynb
    └── feature_engineering.ipynb
```

---

# ⚙️ Technology Stack

| Layer            | Technologies        |
| ---------------- | ------------------- |
| Programming      | Python              |
| Dashboard        | Streamlit           |
| Database         | SQLite + SQLAlchemy |
| BI Tool          | Microsoft Power BI  |
| Data Processing  | Pandas, NumPy       |
| Visualization    | Plotly, Matplotlib  |
| Machine Learning | Scikit-Learn        |
| Excel Support    | OpenPyXL            |

---

# 📊 Dataset Information

| Dataset     | Records  |
| ----------- | -------- |
| Customers   | 12,000+  |
| Products    | 8,000+   |
| Orders      | 50,000+  |
| Order Items | 150,000+ |

### Data Quality Engine Performs

* Missing Value Detection
* Duplicate Removal
* Datatype Conversion
* Schema Validation
* Foreign Key Validation
* Automatic Column Standardization

---

# 📷 Dashboard Preview

### 🏠 Executive Dashboard

*Add Screenshot Here*

### 📤 Smart Upload Center

*Add Screenshot Here*

### 👥 Customer Analytics Dashboard

*Add Screenshot Here*

### 📊 Power BI Executive Dashboard

*Add Screenshot Here*

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/CommerceIQ.git
cd CommerceIQ
```

## Create Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Application

```bash
streamlit run app.py
```

Application launches locally.

---

# 🌐 Deployment

CommerceIQ is deployment-ready on **Streamlit Community Cloud**.

### Deployment Steps

1. Push project to GitHub.
2. Connect repository with Streamlit Cloud.
3. Set `app.py` as entry point.
4. Add environment variable:

```env
DATABASE_URL=sqlite:///database/commerceiq.db
```

5. Deploy.

---

# 📈 Business Impact

CommerceIQ helps organizations:

* Increase customer retention through RFM segmentation.
* Identify top revenue generating products.
* Reduce manual database operations using automated uploads.
* Improve operational reporting with live dashboards.
* Generate AI-driven business recommendations for decision making.

---

# 🎓 Skills Demonstrated

### Data Analytics

* SQL Analytics
* KPI Design
* Customer Analytics
* Product Analytics
* Sales Analytics

### Data Engineering

* ETL Pipeline
* Data Cleaning
* Schema Validation
* SQLite Database Management

### Business Intelligence

* Power BI
* Interactive Dashboards
* Executive Reporting
* Drill Down Analytics

### Python

* Streamlit
* Pandas
* SQLAlchemy
* Plotly
* NumPy

---

# 🏆 Resume Impact

**CommerceIQ** demonstrates experience across:

* End-to-End Data Analytics Project
* Business Intelligence Development
* Data Engineering Workflow
* Dashboard Development
* SQL Database Management
* AI-assisted Business Decision Support

Suitable for roles including:

* Data Analyst
* Business Analyst
* BI Analyst
* Analytics Engineer
* Product Analyst

---

# 👨‍💻 Author

## Aditya Sharma

**Aspiring Data Analyst | Business Analyst | BI Developer**

**Tech Stack**

Python • SQL • Power BI • Streamlit • Pandas • Machine Learning

---

<p align="center">
⭐ If this project helped you or inspired you, consider giving it a Star on GitHub.
</p>
