import random
import time
from datetime import datetime

from sqlalchemy.orm import Session

from database import engine
from models import Customer, Product, Order, OrderItem

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "PayPal",
    "Cash on Delivery"
]

ORDER_STATUS = [
    "Delivered",
    "Delivered",
    "Delivered",
    "Delivered",
    "Shipped",
    "Processing",
    "Cancelled"
]


def weighted_products(products):
    """
    Higher rated products have higher probability of being sold.
    """

    weights = []

    for p in products:

        weight = max(1, int(p.rating * 10))

        if p.stock > 0:
            weights.append(weight)
        else:
            weights.append(0)

    return weights


def generate_order():

    session = Session(engine)

    try:

        customers = session.query(Customer).all()
        available_products = session.query(Product).filter(Product.stock > 0).all()

        if not customers:
            print("No customers found.")
            return

        if not available_products:
            print("No products in stock.")
            return

        customer = random.choice(customers)

        order = Order(
            customer_id=customer.customer_id,
            order_date=datetime.now(),
            payment_method=random.choice(PAYMENT_METHODS),
            status=random.choice(ORDER_STATUS),

            discount=0.0,
            tax=0.0,
            shipping=0.0,

            total_amount=0.0,
            net_amount=0.0
        )

        session.add(order)
        session.flush()

        weights = weighted_products(available_products)

        selected_products = random.choices(
            available_products,
            weights=weights,
            k=random.randint(1, 5)
        )

        # Remove duplicates
        selected_products = list(
            {p.product_id: p for p in selected_products}.values()
        )

        subtotal = 0.0

        for product in selected_products:

            if product.stock <= 0:
                continue

            qty = random.randint(1, min(product.stock, 3))

            line_total = qty * product.price

            item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=qty,
                unit_price=product.price,
                line_total=line_total
            )

            session.add(item)

            product.stock -= qty

            subtotal += line_total

        # Business calculations
        discount = round(subtotal * 0.05, 2)

        taxable_amount = subtotal - discount

        tax = round(taxable_amount * 0.18, 2)

        shipping = 50 if subtotal < 500 else 0

        net_amount = taxable_amount + tax + shipping

        order.total_amount = round(subtotal, 2)
        order.discount = discount
        order.tax = tax
        order.shipping = shipping
        order.net_amount = round(net_amount, 2)

        session.commit()

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"Order #{order.order_id} | "
            f"Items: {len(selected_products)} | "
            f"Subtotal: ₹{order.total_amount:.2f} | "
            f"Net: ₹{order.net_amount:.2f}"
        )

    except Exception as e:

        session.rollback()
        print(f"Error: {e}")

    finally:

        session.close()

def generate_orders(n=100):

    print(f"\nGenerating {n} Orders...\n")

    for _ in range(n):
        generate_order()

    print("\nDone.\n")

def live_orders():

    print("=" * 60)
    print("LIVE ORDER STREAM STARTED")
    print("=" * 60)

    while True:

        generate_order()

        time.sleep(random.randint(3, 8))


if __name__ == "__main__":

    print("="*60)
    print("🚀 AI COMMERCE LIVE TRANSACTION ENGINE")
    print("="*60)

    print("Starting automatic order generation...")

    live_orders()