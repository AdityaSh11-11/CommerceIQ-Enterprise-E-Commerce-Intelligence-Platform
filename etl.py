from sqlalchemy.orm import Session

from database import engine
from models import Product
from models import Customer

from utils import get_json

PRODUCT_URL = "https://dummyjson.com/products?limit=200"

def fetch_products():
    data = get_json(PRODUCT_URL)
    return data["products"]

USER_URL = "https://dummyjson.com/users?limit=200"

def fetch_customers():
    data = get_json(USER_URL)
    return data["users"]

def load_products():

    session = Session(engine)

    products = fetch_products()

    inserted = 0
    updated = 0

    for p in products:

        db_product = session.get(Product, p["id"])

        if db_product:

            db_product.price = p["price"]
            db_product.stock = p["stock"]
            db_product.rating = p["rating"]

            updated += 1

        else:

            product = Product(

                product_id=p["id"],

                title=p["title"],

                category=p["category"],

                brand=p.get("brand", "Unknown"),

                price=p["price"],

                rating=p["rating"],

                stock=p["stock"]

            )

            session.add(product)

            inserted += 1

    session.commit()

    session.close()

    print(f"Products Inserted : {inserted}")
    print(f"Products Updated  : {updated}")


def load_customers():

    session = Session(engine)

    users = fetch_customers()

    inserted = 0

    for u in users:

        exists = session.get(Customer, u["id"])

        if exists:
            continue

        customer = Customer(

            customer_id=u["id"],

            first_name=u["firstName"],

            last_name=u["lastName"],

            email=u["email"],

            city=u["address"]["city"],

            country=u["address"]["country"]

        )

        session.add(customer)

        inserted += 1

    session.commit()

    session.close()

    print(f"Customers Inserted : {inserted}")

if __name__ == "__main__":

    print("=" * 50)

    print("Running ETL")

    print("=" * 50)

    load_products()

    load_customers()

    print("=" * 50)

    print("ETL Finished")