from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from database import engine
from models import (
    Order,
    OrderItem,
    Customer,
    DailyMetric
)

from datetime import datetime

from sqlalchemy import func

def total_revenue(session):
    return session.query(
        func.coalesce(func.sum(Order.net_amount), 0.0)
    ).scalar()

def total_orders(session):

    return session.query(Order).count()

def total_customers(session):

    return session.query(Customer).count()

def average_order_value(session):

    revenue = total_revenue(session)

    orders = total_orders(session)

    if orders == 0:
        return 0

    return revenue / orders

def total_products_sold(session):
    return session.query(
        func.coalesce(func.sum(OrderItem.quantity), 0)
    ).scalar()

from sqlalchemy.orm import Session
from datetime import datetime

def refresh_daily_metrics():

    session = Session(engine)

    try:

        today = datetime.now().strftime("%Y-%m-%d")

        # Calculate ALL metrics FIRST
        revenue = total_revenue(session)
        orders = total_orders(session)
        customers = total_customers(session)
        aov = average_order_value(session)
        products = total_products_sold(session)

        metric = session.get(DailyMetric, today)

        if metric is None:

            metric = DailyMetric(
                date=today,
                revenue=revenue,
                total_orders=orders,
                total_customers=customers,
                avg_order_value=aov,
                total_products_sold=products
            )

            session.add(metric)

        else:

            metric.revenue = revenue
            metric.total_orders = orders
            metric.total_customers = customers
            metric.avg_order_value = aov
            metric.total_products_sold = products

        session.commit()

        print("Daily Metrics Updated")

    except Exception as e:

        session.rollback()
        print(e)

    finally:

        session.close()
if __name__ == "__main__":

    refresh_daily_metrics()