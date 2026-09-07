from apscheduler.schedulers.blocking import BlockingScheduler

from etl import load_products, load_customers
from transaction_engine import generate_orders
from inventory import restock_products

scheduler = BlockingScheduler()


def run_etl():

    print("\n========== ETL ==========")

    load_products()
    load_customers()

    print("ETL Finished")


def run_orders():

    print("\n====== New Orders ======")

    generate_orders(20)

    print("Orders Generated")

def run_inventory():

    print("\nInventory Check")

    restock_products()

scheduler.add_job(
    run_inventory,
    "interval",
    minutes=2
)
scheduler.add_job(
    run_etl,
    "interval",
    minutes=60
)

scheduler.add_job(
    run_orders,
    "interval",
    seconds=20
)

print("=" * 60)
print("Scheduler Started")
print("=" * 60)

scheduler.start()