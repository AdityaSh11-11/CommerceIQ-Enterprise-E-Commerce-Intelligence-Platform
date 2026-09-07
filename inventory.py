from sqlalchemy.orm import Session

from database import engine
from models import Product

LOW_STOCK = 10

RESTOCK_TO = 100


def restock_products():

    session = Session(engine)

    products = (
        session.query(Product)
        .filter(Product.stock <= LOW_STOCK)
        .all()
    )

    if not products:
        print("No products need restocking.")
        session.close()
        return

    print("\nRestocking Products")

    for product in products:

        old_stock = product.stock

        setattr(product, "stock", RESTOCK_TO)

        print(
            f"{product.title[:30]:30} "
            f"{old_stock} -> {RESTOCK_TO}"
        )

    session.commit()

    session.close()

    print("Restocking Complete")