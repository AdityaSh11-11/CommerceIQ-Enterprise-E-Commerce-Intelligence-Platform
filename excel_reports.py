from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.formatting.rule import CellIsRule
import os

# ==========================================================
# COLORS & STYLES
# ==========================================================

HEADER_FILL = PatternFill("solid", fgColor="1E3A8A")
GREEN_FILL = PatternFill("solid", fgColor="16A34A")
RED_FILL = PatternFill("solid", fgColor="DC2626")
ORANGE_FILL = PatternFill("solid", fgColor="F59E0B")
LIGHT_FILL = PatternFill("solid", fgColor="E0F2FE")

HEADER_FONT = Font(color="FFFFFF", bold=True, size=12)
TITLE_FONT = Font(color="1E3A8A", bold=True, size=16)
BOLD_FONT = Font(bold=True)

CENTER = Alignment(horizontal="center", vertical="center")

THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def style_headers(sheet):
    """Style first row."""
    for cell in sheet[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = THIN_BORDER

def autofit_columns(sheet):
    for col in sheet.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        sheet.column_dimensions[get_column_letter(col[0].column)].width = min(length + 4, 30)

# ==========================================================
# MAIN GENERATOR
# ==========================================================

def generate_excel_report(report_type, orders, customers, products, order_items):

    wb = Workbook()

    # ======================================================
    # DASHBOARD SHEET
    # ======================================================

    dashboard = wb.active
    if dashboard is None:
        raise RuntimeError("Workbook does not have an active worksheet")
    dashboard.title = "Executive Dashboard"

    dashboard["A1"] = "CommerceIQ Executive Business Report"
    dashboard["A1"].font = TITLE_FONT

    revenue = orders["net_amount"].sum()
    orders_count = len(orders)
    profit = revenue - orders["tax"].sum()
    avg_order = revenue / orders_count if orders_count else 0
    low_stock = len(products[products.stock < 20])

    metrics = [
        ("Total Revenue", revenue),
        ("Total Orders", orders_count),
        ("Customers", len(customers)),
        ("Average Order Value", avg_order),
        ("Estimated Profit", profit),
        ("Low Stock Products", low_stock)
    ]

    dashboard.append([])
    dashboard.append(["Metric", "Value"])

    for metric, value in metrics:
        dashboard.append([metric, value])

    style_headers(dashboard)

    for cell in dashboard["B"]:
        if cell.row > 2 and isinstance(cell.value, (int, float)):
            cell.number_format = '₹#,##0.00'

    # ======================================================
    # SALES DATA SHEET
    # ======================================================

    sales_sheet = wb.create_sheet("Sales_Data")

    sales = order_items.merge(products, on="product_id")
    sales["Revenue"] = sales["quantity"] * sales["unit_price"]

    sales_sheet.append(list(sales.columns))

    for row in sales.itertuples(index=False):
        sales_sheet.append(list(row))

    style_headers(sales_sheet)

    # ======================================================
    # CUSTOMER SHEET
    # ======================================================

    customer_sheet = wb.create_sheet("Customer_Data")

    customer_sheet.append(list(customers.columns))

    for row in customers.itertuples(index=False):
        customer_sheet.append(list(row))

    style_headers(customer_sheet)

    # ======================================================
    # INVENTORY SHEET
    # ======================================================

    inventory_sheet = wb.create_sheet("Inventory")

    inventory = products.copy()
    inventory["Inventory Value"] = inventory["price"] * inventory["stock"]

    inventory_sheet.append(list(inventory.columns))

    for row in inventory.itertuples(index=False):
        inventory_sheet.append(list(row))

    style_headers(inventory_sheet)

    # Conditional Formatting for Stock
    stock_col = list(inventory.columns).index("stock") + 1
    stock_letter = get_column_letter(stock_col)

    inventory_sheet.conditional_formatting.add(
        f"{stock_letter}2:{stock_letter}{inventory_sheet.max_row}",
        CellIsRule(operator="lessThan", formula=['20'], fill=RED_FILL)
    )

    # ======================================================
    # FINANCIAL SUMMARY SHEET
    # ======================================================

    finance_sheet = wb.create_sheet("Financial_Summary")

    finance_sheet.append([
        "Order ID",
        "Total Amount",
        "Discount",
        "Tax",
        "Shipping",
        "Net Amount"
    ])

    for row in orders[
        ["order_id","total_amount","discount","tax","shipping","net_amount"]
    ].itertuples(index=False):
        finance_sheet.append(list(row))

    style_headers(finance_sheet)

    # ======================================================
    # PIVOT SUMMARY
    # ======================================================

    pivot_sheet = wb.create_sheet("Pivot_Summary")

    category_summary = (
        sales.groupby("category")
        .agg(
            Revenue=("Revenue","sum"),
            Units=("quantity","sum")
        )
        .reset_index()
    )

    pivot_sheet.append(["Category","Revenue","Units Sold"])

    for row in category_summary.itertuples(index=False):
        pivot_sheet.append(list(row))

    style_headers(pivot_sheet)

    # ======================================================
    # RECOMMENDATION SHEET
    # ======================================================

    rec_sheet = wb.create_sheet("Recommendations")

    rec_sheet.append([
        "Product",
        "Current Stock",
        "Recommended Stock",
        "Priority"
    ])

    low_inventory = inventory[inventory.stock < 20]

    for row in low_inventory.itertuples(index=False):
        rec_sheet.append([
            row.title,
            row.stock,
            row.stock + 50,
            "Restock Immediately"
        ])

    style_headers(rec_sheet)

    # ======================================================
    # ADD CHARTS
    # ======================================================

    # Revenue by Category Chart
    bar = BarChart()
    bar.title = "Revenue by Category"

    data = Reference(
        pivot_sheet,
        min_col=2,
        min_row=1,
        max_row=pivot_sheet.max_row
    )

    cats = Reference(
        pivot_sheet,
        min_col=1,
        min_row=2,
        max_row=pivot_sheet.max_row
    )

    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    bar.height = 8
    bar.width = 14

    pivot_sheet.add_chart(bar, "E2")

    # Revenue Trend Chart
    line_sheet = wb.create_sheet("Revenue_Trend")

    daily = (
        orders.groupby(orders.order_date.dt.date)["net_amount"]
        .sum()
        .reset_index()
    )

    line_sheet.append(["Date","Revenue"])

    for row in daily.itertuples(index=False):
        line_sheet.append(list(row))

    style_headers(line_sheet)

    line = LineChart()
    line.title = "Daily Revenue Trend"

    data = Reference(
        line_sheet,
        min_col=2,
        min_row=1,
        max_row=line_sheet.max_row
    )

    cats = Reference(
        line_sheet,
        min_col=1,
        min_row=2,
        max_row=line_sheet.max_row
    )

    line.add_data(data, titles_from_data=True)
    line.set_categories(cats)
    line.height = 8
    line.width = 16

    line_sheet.add_chart(line, "D2")

    # Pie Chart
    pie = PieChart()
    pie.title = "Sales by Category"

    labels = Reference(
        pivot_sheet,
        min_col=1,
        min_row=2,
        max_row=pivot_sheet.max_row
    )

    data = Reference(
        pivot_sheet,
        min_col=2,
        min_row=1,
        max_row=pivot_sheet.max_row
    )

    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    pie.height = 8
    pie.width = 10

    pivot_sheet.add_chart(pie, "E20")

    # ======================================================
    # AUTO FORMAT
    # ======================================================

    for sheet in wb.worksheets:

        autofit_columns(sheet)
        sheet.freeze_panes = "A2"
        sheet.sheet_view.showGridLines = False

        for row in sheet.iter_rows():
            for cell in row:
                cell.border = THIN_BORDER

    # ======================================================
    # SAVE FILE
    # ======================================================

    os.makedirs("reports", exist_ok=True)

    filename = "reports/CommerceIQ_Excel_Report.xlsx"

    wb.save(filename)

    return filename