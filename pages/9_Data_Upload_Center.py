import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
from config import DATABASE_URL
import json

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Data Upload Center",
    page_icon="📤",
    layout="wide"
)

# Premium Dashboard CSS
with open("dashboard_style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

# ==========================================================
# REFRESH BUTTON FUNCTION
# ==========================================================
def section_header(title, subtitle=""):

    st.markdown(f"""
    <div style='margin-bottom:18px'>
        <h2 style='margin-bottom:4px'>{title}</h2>
        <p style='color:#94A3B8;margin-top:0'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
def refresh_dashboard():
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# ==========================================================
# DATABASE SNAPSHOT
# ==========================================================

@st.cache_data(ttl=20)
def load_database_snapshot():

    tables = ["orders", "customers", "products", "order_items"]

    snapshot = {}

    with engine.connect() as conn:

        for table in tables:

            try:
                total = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()

                snapshot[table] = total

            except Exception:
                snapshot[table] = 0

    return snapshot


snapshot = load_database_snapshot()

# ==========================================================
# SQLITE SCHEMA LOADER
# ==========================================================

@st.cache_data(ttl=60)
def load_schema(table_name):

    return pd.read_sql(
        f"PRAGMA table_info({table_name})",
        engine
    )


# ==========================================================
# TABLE DETECTION SCHEMA
# ==========================================================

TABLE_SCHEMAS = {

    "orders": {
        "customer_id",
        "payment_method",
        "status",
        "discount",
        "tax",
        "shipping",
        "total_amount",
        "net_amount",
        "order_date"
    },

    "customers": {
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "city",
        "country",
        "zipcode"
    },

    "products": {
        "product_id",
        "title",
        "category",
        "brand",
        "price",
        "stock",
        "rating"
    },

    "order_items": {
        "order_id",
        "product_id",
        "quantity",
        "unit_price"
    }
}

# ==========================================================
# AUTO DETECT SQLITE TABLE
# ==========================================================

def detect_table(df):

    cols = set(
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
    )

    score: dict[str, int] = {}

    for table, schema in TABLE_SCHEMAS.items():
        score[table] = len(cols.intersection(schema))

    detected = max(score, key=lambda table: score[table])

    return detected, score

# ==========================================================
# DATA CLEANING ENGINE
# ==========================================================

def clean_dataframe(df):

    clean = df.copy()

    clean.columns = (
        clean.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
    )

    clean.replace(["", " ", "NA", "N/A"], np.nan, inplace=True)

    before_duplicates = len(clean)

    clean.drop_duplicates(inplace=True)

    duplicates_removed = before_duplicates - len(clean)

    for col in clean.columns:

        name = col.lower()

        if "date" in name:

            clean[col] = pd.to_datetime(
                clean[col],
                errors="coerce"
            )

        elif "email" in name:

            clean[col] = (
                clean[col]
                .astype(str)
                .str.lower()
                .str.strip()
            )

        elif any(
            x in name
            for x in [
                "price",
                "amount",
                "discount",
                "shipping",
                "tax",
                "rating",
                "net"
            ]
        ):

            clean[col] = pd.to_numeric(
                clean[col],
                errors="coerce"
            )

        elif any(
            x in name
            for x in [
                "id",
                "stock",
                "quantity"
            ]
        ):

            clean[col] = pd.to_numeric(
                clean[col],
                errors="coerce"
            ).astype("Int64")

    return clean, duplicates_removed


# Backward-compatible alias used by upload actions.
def clean_dataset(df, table_name=None):
    """Normalize and clean a dataset before SQLite upload."""
    cleaned_df, _ = clean_dataframe(df)
    return cleaned_df

# ==========================================================
# HERO SECTION
# ==========================================================
st.html("""
<div class="hero-small">
    <div class="hero-chip">COMMERCEIQ ADMIN PORTAL</div>

    <h1>Enterprise Data Upload Center</h1>

    <p>
        Upload CSV or Excel datasets, automatically clean and validate records,
        insert them into the correct SQLite tables, preview live data,
        rollback uploads, and manage CommerceIQ database operations —
        all from one enterprise-grade admin console.
    </p>
</div>
""")

# ==========================================================
# REFRESH BUTTON
# ==========================================================

top1, top2 = st.columns([8,2])

with top2:

    if st.button(
        "🔄 Refresh Dashboard",
        use_container_width=True
    ):
        refresh_dashboard()

st.divider()

# ==========================================================
# DATABASE SNAPSHOT CARDS
# ==========================================================

st.markdown("## SQLite Database Snapshot")
st.caption("Live overview of CommerceIQ operational database.")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Orders", f"{snapshot['orders']:,}")
c2.metric("Customers", f"{snapshot['customers']:,}")
c3.metric("Products", f"{snapshot['products']:,}")
c4.metric("Order Items", f"{snapshot['order_items']:,}")

st.divider()

# ==========================================================
# MAIN TABS
# ==========================================================

upload_tab, manual_tab, preview_tab, admin_tab = st.tabs([
    "📤 Smart Upload Center",
    "✍️ Manual SQLite Entry",
    "🗄️ Live Database Preview",
    "⚙️ Admin Tools"
])

# ==========================================================
# PART 2 — SMART BULK UPLOAD CENTER
# ==========================================================

# Upload History (Session Based)
if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

if "last_upload" not in st.session_state:
    st.session_state.last_upload = None


# ----------------------------------------------------------
# AUTO MAP DATAFRAME TO SQLITE TABLE
# ----------------------------------------------------------

def map_dataframe_to_schema(df, table_name):

    upload_df = df.copy()

    upload_df.columns = (
        upload_df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
    )

    # ---------------- CUSTOMERS ---------------- #

    if table_name == "customers":

        if "customer_name" in upload_df.columns:

            names = (
                upload_df["customer_name"]
                .fillna("")
                .astype(str)
                .str.split(" ", n=1, expand=True)
            )

            upload_df["first_name"] = names[0]
            upload_df["last_name"] = names[1].fillna("")

        keep_cols = [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "city",
            "country",
            "zipcode"
        ]

        upload_df = upload_df[[c for c in keep_cols if c in upload_df.columns]]

    # ---------------- PRODUCTS ---------------- #

    elif table_name == "products":

        rename_map = {
            "product_title": "title",
            "unit_price": "price"
        }

        upload_df.rename(columns=rename_map, inplace=True)

        if "stock" not in upload_df.columns:
            upload_df["stock"] = 100

        keep_cols = [
            "product_id",
            "title",
            "category",
            "brand",
            "price",
            "stock",
            "rating"
        ]

        upload_df = upload_df[[c for c in keep_cols if c in upload_df.columns]]

    # ---------------- ORDERS ---------------- #

    elif table_name == "orders":

        keep_cols = [
            "order_id",
            "customer_id",
            "payment_method",
            "status",
            "discount",
            "tax",
            "shipping",
            "total_amount",
            "net_amount",
            "order_date"
        ]

        upload_df = upload_df[[c for c in keep_cols if c in upload_df.columns]]

        if "order_date" in upload_df.columns:
            upload_df["order_date"] = pd.to_datetime(
                upload_df["order_date"],
                errors="coerce"
            )

    # ---------------- ORDER ITEMS ---------------- #

    elif table_name == "order_items":

        keep_cols = [
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
        ]

        upload_df = upload_df[[c for c in keep_cols if c in upload_df.columns]]

    return upload_df


# ----------------------------------------------------------
# VALIDATE SQLITE SCHEMA
# ----------------------------------------------------------

def validate_schema(df, table_name):

    schema = load_schema(table_name)

    sqlite_cols = schema["name"].tolist()

    upload_cols = df.columns.tolist()

    missing = [c for c in sqlite_cols if c not in upload_cols]

    extra = [c for c in upload_cols if c not in sqlite_cols]

    return sqlite_cols, upload_cols, missing, extra


# ----------------------------------------------------------
# BULK INSERT (Chunk Upload)
# ----------------------------------------------------------

def upload_dataframe(df, table_name):

    CHUNK_SIZE = 5000

    # Primary Key Mapping
    PK_MAP = {
        "orders": "order_id",
        "customers": "customer_id",
        "products": "product_id",
        "order_items": None
    }

    pk = PK_MAP.get(table_name)

    inserted = 0
    skipped = 0

    upload_df = df.copy()

    # Skip duplicate primary keys
    if pk and pk in upload_df.columns:

        existing_ids = pd.read_sql(
            f"SELECT {pk} FROM {table_name}",
            engine
        )[pk]

        upload_df = upload_df[
            ~upload_df[pk].isin(existing_ids)
        ]

        skipped = len(df) - len(upload_df)

    with engine.begin() as conn:

        for start in range(0, len(upload_df), CHUNK_SIZE):

            chunk = upload_df.iloc[start:start+CHUNK_SIZE]

            chunk.to_sql(
                table_name,
                conn,
                if_exists="append",
                index=False,
                method="multi"
            )

            inserted += len(chunk)

    return inserted, skipped


# ==========================================================
# BULK UPLOAD UI
# ==========================================================

with upload_tab:

    st.markdown("## Smart CSV / Excel Upload Center")
    st.caption(
        "CommerceIQ AI automatically detects the destination SQLite table, "
        "cleans your dataset and validates it before inserting."
    )

    uploaded_file = st.file_uploader(
        "📂 Upload CSV or Excel Dataset",
        type=["csv", "xlsx"],
        key="smart_upload"
    )

    raw_df = None

    detected_table = None

    mapped_df = None

    if uploaded_file is not None:

        try:

            if uploaded_file.name.endswith(".csv"):
                raw_df = pd.read_csv(uploaded_file)

            else:
                raw_df = pd.read_excel(uploaded_file)

            st.success(
                f"Dataset Loaded Successfully — {len(raw_df):,} Rows"
            )

        except Exception as e:
            st.error(f"Unable to read dataset: {e}")

    # ------------------------------------------------------
    # DETECTION + CLEANING
    # ------------------------------------------------------

    if raw_df is not None:

        detected_table, score = detect_table(raw_df)

        st.markdown("### AI Table Detection Confidence")

        confidence_df = pd.DataFrame({
            "SQLite Table": score.keys(),
            "Matching Columns": score.values()
        }).sort_values("Matching Columns", ascending=False)

        st.dataframe(confidence_df, use_container_width=True)

        st.success(
            f"AI detected `{detected_table.upper()}` "
            f"with {max(score.values())} matching columns."
        )

        cleaned_df, removed_duplicates = clean_dataframe(raw_df)

        mapped_df = map_dataframe_to_schema(
            cleaned_df,
            detected_table
        )

        st.divider()

        st.markdown("### AI Dataset Detection")

        info1, info2, info3 = st.columns(3)

        info1.metric("Detected Table", detected_table.upper())
        info2.metric("Rows", f"{len(cleaned_df):,}")
        info3.metric("Duplicates Removed", removed_duplicates)

        st.success(
            f"CommerceIQ detected this dataset belongs to **{detected_table.upper()}**."
        )

        st.divider()

        # --------------------------------------------------
        # PREVIEW
        # --------------------------------------------------

        st.markdown("### Cleaned Dataset Preview")

        st.dataframe(
            mapped_df.head(20),
            use_container_width=True,
            height=350
        )

        # --------------------------------------------------
        # QUALITY REPORT
        # --------------------------------------------------

        st.markdown("### Data Quality Summary")

        q1, q2, q3, q4 = st.columns(4)

        q1.metric("Rows After Cleaning", f"{len(mapped_df):,}")
        q2.metric("Columns", len(mapped_df.columns))
        q3.metric("Missing Values", int(mapped_df.isna().sum().sum()))
        q4.metric("Duplicate Rows", int(mapped_df.duplicated().sum()))

        st.divider()

        # --------------------------------------------------
        # SQLITE VALIDATION
        # --------------------------------------------------

        sqlite_cols, upload_cols, missing_cols, extra_cols = validate_schema(
            mapped_df,
            detected_table
        )

        # ======================================================
        # SQLITE SCHEMA VALIDATION (PREMIUM UI)
        # ======================================================

        st.markdown("""
        <div class="section-header">
            <h2>🛡️ SQLite Schema Validation</h2>
            <p>CommerceIQ AI compares your uploaded dataset with the selected SQLite table before inserting records.</p>
        </div>
        """, unsafe_allow_html=True)

        left, right = st.columns(2)

        with left:
            st.markdown("""
            <div class="metric-card">
                <h4>📋 SQLite Table Columns</h4>
            </div>
            """, unsafe_allow_html=True)

            st.code("\n".join(sqlite_cols), language="text")

        with right:
            st.markdown("""
            <div class="metric-card">
                <h4>📁 Uploaded Dataset Columns</h4>
            </div>
            """, unsafe_allow_html=True)

            st.code("\n".join(upload_cols), language="text")

        st.markdown("<br>", unsafe_allow_html=True)

        # Validation Summary Cards
        v1, v2, v3 = st.columns(3)

        with v1:
            st.metric("SQLite Columns", len(sqlite_cols))

        with v2:
            st.metric("Uploaded Columns", len(upload_cols))

        with v3:
            st.metric("Schema Match", f"{len(sqlite_cols)-len(missing_cols)}/{len(sqlite_cols)}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Validation Status
        if not missing_cols and not extra_cols:
            st.success("✅ Perfect Match — Dataset is fully compatible with the selected SQLite table.")

        else:
            if missing_cols:
                st.error("❌ Missing Required Columns")
                st.code("\n".join(missing_cols), language="text")

            if extra_cols:
                st.warning("⚠️ Extra Columns Detected (Ignored During Upload)")
                st.code("\n".join(extra_cols), language="text")

        st.divider()

        # --------------------------------------------------
        # IMPORT CONTROLS
        # --------------------------------------------------

        st.markdown("### Import Controls")

        btn1, btn2 = st.columns(2)

        append_btn = btn1.button(
            "🚀 Upload into SQLite",
            type="primary",
            use_container_width=True
        )

        replace_table = btn2.button(
            "⚠ Replace Entire Table",
            use_container_width=True
        )

        # ==============================================
        # APPEND
        # ==============================================

        if append_btn:

            try:

                upload_df = clean_dataset(mapped_df, detected_table)

                # Primary key mapping
                pk_map = {
                    "orders": "order_id",
                    "customers": "customer_id",
                    "products": "product_id",
                    "order_items": None
                }

                pk_column = pk_map[detected_table]

                inserted = 0
                skipped = 0

                if pk_column:
                    # Existing IDs from SQLite
                    existing_ids = pd.read_sql(
                        f"SELECT {pk_column} FROM {detected_table}",
                        engine
                    )[pk_column]

                    # Keep only new records
                    new_df = upload_df[
                        ~upload_df[pk_column].isin(existing_ids)
                    ].copy()

                    skipped = len(upload_df) - len(new_df)

                else:
                    new_df = upload_df.copy()

                if not new_df.empty:
                    new_df.to_sql(
                        detected_table,
                        engine,
                        if_exists="append",
                        index=False,
                        chunksize=5000,
                        method="multi"
                    )
                    inserted = len(new_df)

                st.success(f"✅ {inserted:,} new records inserted into `{detected_table}`.")

                if skipped:
                    st.info(f"⏭️ {skipped:,} duplicate records skipped automatically.")

                # Save upload history for Undo feature
                primary_key = {
                    "orders":"order_id",
                    "customers":"customer_id",
                    "products":"product_id",
                    "order_items":None
                }.get(detected_table)

                uploaded_ids = []

                if primary_key and primary_key in mapped_df.columns:
                    uploaded_ids = mapped_df[primary_key].tolist()

                st.session_state.last_upload = {
                    "table": detected_table,
                    "rows": inserted,
                    "ids": uploaded_ids,
                    "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
}

                st.session_state.upload_history.append(st.session_state.last_upload)

                st.cache_data.clear()

            except Exception as e:
                st.error(f"Upload Failed : {e}")
        # ==============================================
        # REPLACE TABLE
        # ==============================================

        if replace_table:

            try:

                with engine.begin() as conn:

                    conn.execute(
                        text(f"DELETE FROM {detected_table}")
                    )

                upload_dataframe(mapped_df, detected_table)

                st.success(
                    f"`{detected_table}` replaced successfully with {len(mapped_df):,} records."
                )

                st.cache_data.clear()

            except Exception as e:

                st.error(f"Replace Failed : {e}")


        # ==========================================================
# PART 3 — DYNAMIC SQLITE MANUAL ENTRY CENTER
# ==========================================================

# ----------------------------------------------------------
# GET FOREIGN KEY VALUES
# ----------------------------------------------------------

@st.cache_data(ttl=30)
def get_dropdown_values():

    dropdowns = {}

    try:
        dropdowns["customer_id"] = pd.read_sql(
            "SELECT customer_id FROM customers ORDER BY customer_id",
            engine
        )["customer_id"].tolist()
    except Exception:
        dropdowns["customer_id"] = []

    try:
        dropdowns["product_id"] = pd.read_sql(
            "SELECT product_id FROM products ORDER BY product_id",
            engine
        )["product_id"].tolist()
    except Exception:
        dropdowns["product_id"] = []

    try:
        dropdowns["order_id"] = pd.read_sql(
            "SELECT order_id FROM orders ORDER BY order_id",
            engine
        )["order_id"].tolist()
    except Exception:
        dropdowns["order_id"] = []

    return dropdowns


dropdown_values = get_dropdown_values()

# ----------------------------------------------------------
# SQLITE TYPE → STREAMLIT INPUT
# ----------------------------------------------------------

def generate_input(column_name, sqlite_type):

    name = column_name.lower()
    dtype = sqlite_type.upper()

    # ---------------- Foreign Keys ----------------

    if name == "customer_id":
        options = dropdown_values["customer_id"]

        if options:
            return st.selectbox("Customer ID", options)

        return st.number_input("Customer ID", min_value=1, step=1)

    if name == "product_id":
        options = dropdown_values["product_id"]

        if options:
            return st.selectbox("Product ID", options)

        return st.number_input("Product ID", min_value=1, step=1)

    if name == "order_id":
        options = dropdown_values["order_id"]

        if options:
            return st.selectbox("Order ID", options)

        return st.number_input("Order ID", min_value=1, step=1)

    # ---------------- Date ----------------

    if "date" in name:
        return pd.to_datetime(
            st.date_input(
                column_name.replace("_", " ").title(),
                value=datetime.today()
            )
        )

    # ---------------- Status ----------------

    if name == "status":
        return st.selectbox(
            "Order Status",
            [
                "Pending",
                "Processing",
                "Shipped",
                "Delivered",
                "Cancelled"
            ]
        )

    # ---------------- Payment ----------------

    if "payment" in name:
        return st.selectbox(
            "Payment Method",
            [
                "UPI",
                "Credit Card",
                "Debit Card",
                "Net Banking",
                "Cash on Delivery"
            ]
        )

    # ---------------- Country ----------------

    if name == "country":
        return st.selectbox(
            "Country",
            [
                "India",
                "United States",
                "Canada",
                "United Kingdom",
                "Australia"
            ]
        )

    # ---------------- Rating ----------------

    if name == "rating":
        return st.slider("Rating", 0.0, 5.0, 4.5, 0.5)

    # ---------------- Integer Fields ----------------

    if (
        "INT" in dtype or
        "quantity" in name or
        "stock" in name
    ):
        return st.number_input(
            column_name.replace("_", " ").title(),
            min_value=0,
            step=1
        )

    # ---------------- Numeric Fields ----------------

    if any(
        word in name
        for word in [
            "price",
            "amount",
            "discount",
            "shipping",
            "tax",
            "net"
        ]
    ):
        return st.number_input(
            column_name.replace("_", " ").title(),
            min_value=0.0,
            step=100.0,
            format="%.2f"
        )

    # ---------------- Email ----------------

    if "email" in name:
        return st.text_input("Email Address")

    # ---------------- Default Text ----------------

    return st.text_input(column_name.replace("_", " ").title())


# ==========================================================
# MANUAL ENTRY TAB UI
# ==========================================================

with manual_tab:

    st.markdown("## Dynamic SQLite Manual Entry")
    st.caption(
        "CommerceIQ automatically builds the input form from the SQLite schema."
    )

    selected_table = st.selectbox(
        "Select Table",
        ["orders", "customers", "products", "order_items"],
        key="manual_entry_table"
    )

    schema_df = load_schema(selected_table)

    # Remove Auto Increment Primary Key
    editable_columns = schema_df[schema_df["pk"] == 0]

    st.success(
        f"Editing Table : {selected_table.upper()} ({len(editable_columns)} editable fields)"
    )

    with st.form(
        key=f"{selected_table}_manual_form",
        clear_on_submit=True
    ):

        st.markdown("### Add New Record")

        values = {}

        cols = st.columns(2)

        for idx, (_, row) in enumerate(editable_columns.iterrows()):

            column = row["name"]
            dtype = row["type"]

            with cols[idx % 2]:

                values[column] = generate_input(column, dtype)

        # --------------------------------------------------
        # AUTO CALCULATE NET AMOUNT
        # --------------------------------------------------

        if selected_table == "orders":

            total = float(values.get("total_amount", 0))
            discount = float(values.get("discount", 0))
            tax = float(values.get("tax", 0))
            shipping = float(values.get("shipping", 0))

            values["net_amount"] = total - discount + tax + shipping

            st.markdown("---")

            st.metric(
                "Calculated Net Amount",
                f"₹ {values['net_amount']:,.2f}"
            )

        submit_manual = st.form_submit_button(
            "🚀 Insert Record into SQLite",
            use_container_width=True
        )

    # ------------------------------------------------------
    # INSERT RECORD
    # ------------------------------------------------------

    if submit_manual:

        try:

            insert_df = pd.DataFrame([values])

            insert_df.to_sql(
                selected_table,
                engine,
                if_exists="append",
                index=False
            )

            st.success(
                f"Record inserted successfully into `{selected_table}`."
            )

            st.balloons()

            st.cache_data.clear()

        except Exception as e:

            st.error(f"Database Error : {e}")

        # ======================================================
        # SQLITE SCHEMA VIEWER (PREMIUM UI)
        # ======================================================

        st.divider()

        st.markdown("""
        <div class="section-header">
            <h2>🗂️ SQLite Schema Viewer</h2>
            <p>Live schema of the selected CommerceIQ SQLite table including column names, data types, primary keys and required fields.</p>
        </div>
        """, unsafe_allow_html=True)

        # ---------- Schema Metrics ----------

        pk_count = int(schema_df["pk"].sum())
        required_count = int(schema_df["notnull"].sum())
        optional_count = len(schema_df) - required_count

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Total Columns", len(schema_df))
        m2.metric("Primary Keys", pk_count)
        m3.metric("Required Fields", required_count)
        m4.metric("Optional Fields", optional_count)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------- Schema Table ----------

        schema_view = schema_df[["name", "type", "pk", "notnull"]].copy()

        schema_view.columns = [
            "Column Name",
            "SQLite Type",
            "Primary Key",
            "Required"
        ]

        schema_view["Primary Key"] = schema_view["Primary Key"].apply(
            lambda x: "🟢 Yes" if x == 1 else "—"
        )

        schema_view["Required"] = schema_view["Required"].apply(
            lambda x: "✅ Required" if x == 1 else "⚪ Optional"
        )

        st.dataframe(
            schema_view,
            use_container_width=True,
            hide_index=True,
            height=340
        )

        st.markdown("<br>", unsafe_allow_html=True)

# ---------- Required vs Optional ----------

required = schema_df.loc[schema_df["notnull"] == 1, "name"].tolist()
optional = schema_df.loc[schema_df["notnull"] == 0, "name"].tolist()

req_col, opt_col = st.columns(2)

with req_col:
    st.markdown("""
    <div class="metric-card">
        <h4>✅ Required Fields</h4>
    </div>
    """, unsafe_allow_html=True)

    required_df = pd.DataFrame({
        "Field": required
    })

    st.dataframe(
        required_df,
        use_container_width=True,
        hide_index=True,
        height=240
    )

with opt_col:
    st.markdown("""
    <div class="metric-card">
        <h4>⚪ Optional Fields</h4>
    </div>
    """, unsafe_allow_html=True)

    optional_df = pd.DataFrame({
        "Field": optional
    })

    st.dataframe(
        optional_df,
        use_container_width=True,
        hide_index=True,
        height=240
    )

st.divider()



    # ==========================================================
# PART 4 — LIVE DATABASE PREVIEW CENTER
# ==========================================================

with preview_tab:

    st.markdown("## Live SQLite Database Preview")
    st.caption(
        "Browse, search, filter, export and delete records from CommerceIQ database."
    )

    # ------------------------------------------------------
    # LOAD TABLE DATA
    # ------------------------------------------------------

    @st.cache_data(ttl=15)
    def load_table_data(table):
        try:
            return pd.read_sql(f"SELECT * FROM {table}", engine)
        except Exception:
            return pd.DataFrame()

    preview_df = load_table_data(selected_table)
    schema = load_schema(selected_table)

    # ------------------------------------------------------
    # SNAPSHOT CARDS
    # ------------------------------------------------------

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Records", f"{len(preview_df):,}")
    m2.metric("Columns", len(preview_df.columns))
    m3.metric("Table", selected_table.upper())
    memory = round(preview_df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    m4.metric("Memory Usage", f"{memory} MB")

    st.divider()

    # ------------------------------------------------------
    # SEARCH + PAGE SIZE
    # ------------------------------------------------------

    left, right = st.columns([4, 1])

    with left:
        search = st.text_input(
            "🔍 Search Records",
            placeholder="Search by customer, email, city, order id, product..."
        )

    with right:
        page_size = st.selectbox(
            "Rows",
            [10, 25, 50, 100, 250],
            index=2
        )

    filtered_df = preview_df.copy()

    if search:

        mask = filtered_df.astype(str).apply(
            lambda col: col.str.contains(
                search,
                case=False,
                na=False
            )
        )

        filtered_df = filtered_df[mask.any(axis=1)]

    st.success(f"Showing {len(filtered_df):,} matching records.")

    # ------------------------------------------------------
    # OPTIONAL FILTERS
    # ------------------------------------------------------

    if not filtered_df.empty:

        filter_columns = st.multiselect(
            "🎯 Filter Columns",
            filtered_df.columns.tolist()
        )

        for col in filter_columns:

            unique_values = (
                filtered_df[col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if len(unique_values) <= 25:

                selected_values = st.multiselect(
                    f"{col}",
                    unique_values
                )

                if selected_values:
                    filtered_df = filtered_df[
                        filtered_df[col].astype(str).isin(selected_values)
                    ]

    st.divider()

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    total_pages = max(
        (len(filtered_df) - 1) // page_size + 1,
        1
    )

    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

    start = (page - 1) * page_size
    end = start + page_size

    st.dataframe(
        filtered_df.iloc[start:end],
        use_container_width=True,
        height=520
    )

    st.caption(
        f"Page {page} of {total_pages} • Showing rows {start+1}-{min(end,len(filtered_df))}"
    )

    st.divider()

    # ------------------------------------------------------
    # EXPORT CSV
    # ------------------------------------------------------

    st.markdown("### Export Current View")

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        "📥 Download Filtered CSV",
        csv,
        file_name=f"{selected_table}_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()

    # ======================================================
    # DELETE RECORD BY PRIMARY KEY
    # ======================================================

    st.markdown("## Delete Record by Primary Key")
    st.caption(
        "Safely remove a single record from the selected SQLite table."
    )

    pk_columns = schema[schema["pk"] == 1]["name"].tolist()

    if pk_columns and not preview_df.empty:

        primary_key = pk_columns[0]

        delete_value = st.selectbox(
            f"Select {primary_key}",
            preview_df[primary_key].tolist(),
            key=f"delete_pk_{selected_table}"
        )

        confirm_delete = st.checkbox(
            f"Confirm delete {primary_key} = {delete_value}",
            key=f"confirm_delete_{selected_table}"
        )

        if st.button(
            "🗑 Delete Selected Record",
            type="primary",
            use_container_width=True
        ):

            if not confirm_delete:

                st.warning("Please confirm before deleting.")

            else:

                try:

                    with engine.begin() as conn:

                        conn.execute(
                            text(
                                f"DELETE FROM {selected_table} WHERE {primary_key}=:id"
                            ),
                            {"id": delete_value}
                        )

                    st.success(
                        f"Record `{delete_value}` deleted successfully."
                    )

                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:

                    st.error(f"Delete Failed: {e}")

    else:

        st.info("Primary key not available for this table.")


    # ==========================================================
# PART 5 — ENTERPRISE ADMIN TOOLS
# ==========================================================

st.divider()

st.markdown("""
## Enterprise Admin Operations Center
Safe database administration tools for CommerceIQ.
""")

admin_tab1, admin_tab2, admin_tab3 = st.tabs([
    "↩️ Undo Last Upload",
    "🗑️ Delete Order by Order ID",
    "💥 Danger Zone"
])

# ==========================================================
# TAB 1 — UNDO LAST BULK UPLOAD
# ==========================================================

with admin_tab1:

    st.markdown("### Undo Last Uploaded Dataset")

    if st.session_state.last_upload:

        upload_info = st.session_state.last_upload

        info1, info2, info3 = st.columns(3)

        info1.metric("Last Upload Table", upload_info["table"].upper())
        info2.metric("Rows Uploaded", upload_info["rows"])
        info3.metric("Uploaded At", upload_info["timestamp"])

        st.warning(
            "Undo removes only the most recently uploaded rows "
            "from the selected table."
        )

        confirm_undo = st.checkbox(
            "I understand the last uploaded dataset will be removed."
        )

        if st.button(
            "↩️ Undo Last Upload",
            use_container_width=True,
            type="primary"
        ):

            if not confirm_undo:
                st.warning("Please confirm undo first.")

            else:

                try:

                    table = upload_info["table"]
                    rows = upload_info["rows"]

                    pk_df = pd.read_sql(
                        f"PRAGMA table_info({table})",
                        engine
                    )

                    pk = pk_df[pk_df["pk"] == 1]["name"].iloc[0]

                    with engine.begin() as conn:

                        conn.execute(text(f"""
                            DELETE FROM {table}
                            WHERE {pk} IN (
                                SELECT {pk}
                                FROM {table}
                                ORDER BY {pk} DESC
                                LIMIT {rows}
                            )
                        """))

                    st.success(
                        f"Successfully removed last {rows} uploaded rows from `{table}`."
                    )

                    st.session_state.last_upload = None
                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:

                    st.error(f"Undo Failed: {e}")

    else:

        st.info("No upload available to undo.")

    st.divider()

    st.markdown("### Upload History")

    if st.session_state.upload_history:

        history_df = pd.DataFrame(st.session_state.upload_history)

        history_df.columns = [
            "Table",
            "Rows Uploaded",
            "Timestamp"
        ]

        st.dataframe(
            history_df.iloc[::-1],
            use_container_width=True,
            height=260
        )

    else:

        st.info("No uploads recorded yet.")

# ==========================================================
# TAB 2 — DELETE ORDER BY ORDER ID
# ==========================================================

with admin_tab2:

    st.markdown("### Delete Order + Related Order Items")

    try:

        orders_df = pd.read_sql("""
            SELECT order_id, customer_id, net_amount, status, order_date
            FROM orders
            ORDER BY order_id DESC
        """, engine)

    except Exception:

        orders_df = pd.DataFrame()

    if orders_df.empty:

        st.info("Orders table is empty.")

    else:

        selected_order = st.selectbox(
            "Select Order ID",
            orders_df["order_id"].tolist()
        )

        preview = orders_df[
            orders_df["order_id"] == selected_order
        ]

        st.dataframe(
            preview,
            use_container_width=True
        )

        confirm_order_delete = st.checkbox(
            f"I want to permanently delete Order #{selected_order}"
        )

        if st.button(
            "🗑️ Delete Selected Order",
            use_container_width=True,
            type="primary"
        ):

            if not confirm_order_delete:

                st.warning("Please confirm deletion.")

            else:

                try:

                    with engine.begin() as conn:

                        conn.execute(
                            text("""
                                DELETE FROM order_items
                                WHERE order_id=:id
                            """),
                            {"id": selected_order}
                        )

                        conn.execute(
                            text("""
                                DELETE FROM orders
                                WHERE order_id=:id
                            """),
                            {"id": selected_order}
                        )

                    st.success(
                        f"Order #{selected_order} deleted successfully."
                    )

                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:

                    st.error(f"Delete Failed: {e}")

# ==========================================================
# TAB 3 — DANGER ZONE
# ==========================================================

with admin_tab3:

    st.error("""
    Danger Zone — Permanent Database Operations

    Tables will remain.
    Only records will be deleted.
    """)

    danger1, danger2 = st.columns(2)

    # ------------------------------------------------------
    # CLEAR SELECTED TABLE
    # ------------------------------------------------------

    with danger1:

        st.markdown("#### Clear Selected Table")

        st.write(
            f"Selected Table: **{selected_table.upper()}**"
        )

        confirm_table = st.checkbox(
            f"Delete ALL records from `{selected_table}`"
        )

        if st.button(
            "🗑️ Clear Selected Table",
            use_container_width=True
        ):

            if not confirm_table:

                st.warning("Confirmation required.")

            else:

                try:

                    with engine.begin() as conn:

                        conn.execute(
                            text(f"DELETE FROM {selected_table}")
                        )

                    st.success(
                        f"All records removed from `{selected_table}`."
                    )

                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:

                    st.error(e)

    # ------------------------------------------------------
    # CLEAR ENTIRE DATABASE
    # ------------------------------------------------------

    with danger2:

        st.markdown("#### Clear Entire CommerceIQ Database")

        st.write("""
        Deletes data from:

        - Orders
        - Order Items
        - Customers
        - Products

        SQLite tables remain intact.
        """)

        confirm_db = st.checkbox(
            "I understand this action is irreversible."
        )

        if st.button(
            "💥 Clear Entire Database",
            use_container_width=True,
            type="primary"
        ):

            if not confirm_db:

                st.warning("Confirmation required.")

            else:

                try:

                    with engine.begin() as conn:

                        conn.execute(text("DELETE FROM order_items"))
                        conn.execute(text("DELETE FROM orders"))
                        conn.execute(text("DELETE FROM customers"))
                        conn.execute(text("DELETE FROM products"))

                    st.success("Entire CommerceIQ database cleared successfully.")

                    st.cache_data.clear()
                    st.rerun()

                except Exception as e:

                    st.error(e)

# ==========================================================
# QUICK DATABASE TOOLS
# ==========================================================

st.divider()

st.markdown("## Quick Database Tools")

tool1, tool2, tool3 = st.columns(3)

with tool1:

    if st.button(
        "🔄 Refresh Database",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()

with tool2:

    if st.button(
        "📊 Reload Current Table",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()

with tool3:

    if st.button(
        "📥 Refresh Snapshot",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()

# ==========================================================
# DATABASE STATUS CARD
# ==========================================================

st.divider()

with st.container(border=True):

    st.markdown("### CommerceIQ Database Status")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Database", "SQLite")
    c2.metric("Active Table", selected_table.upper())
    c3.metric("Tables", len(inspector.get_table_names()))
    c4.metric(
        "Last Refresh",
        datetime.now().strftime("%H:%M:%S")
    )

    st.success("🟢 Database Connected • AI Upload Engine Active")

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.markdown("""
<div class="ai-footer">

<h4>CommerceIQ Enterprise Data Upload Center</h4>

<p>
SQLite Database Management • AI Smart Upload Engine • Dynamic Manual Entry •
Undo Upload • Delete Records • Enterprise Admin Controls
</p>

</div>
""", unsafe_allow_html=True)