from sqlalchemy.orm import Session

from database import engine
from models import Product, Customer

session = Session(engine)

print("=" * 60)
print("DATABASE VALIDATION")
print("=" * 60)

# ----------------------------
# Product Count
# ----------------------------

products = session.query(Product).all()

print(f"Total Products : {len(products)}")

print("\nFirst 5 Products")

for product in products[:5]:
    print(
        f"""
ID       : {product.product_id}
Title    : {product.title}
Category : {product.category}
Brand    : {product.brand}
Price    : ${product.price}
Rating   : {product.rating}
Stock    : {product.stock}
"""
    )

# ----------------------------
# Customer Count
# ----------------------------

customers = session.query(Customer).all()

print("=" * 60)

print(f"Total Customers : {len(customers)}")

print("\nFirst 5 Customers")

for customer in customers[:5]:
    print(
        f"""
ID      : {customer.customer_id}
Name    : {customer.first_name} {customer.last_name}
Email   : {customer.email}
City    : {customer.city}
Country : {customer.country}
"""
    )

print("=" * 60)

session.close()