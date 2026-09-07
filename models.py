from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


# ==========================
# Customer
# ==========================

class Customer(Base):

    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String)

    last_name: Mapped[str] = mapped_column(String)

    email: Mapped[str] = mapped_column(String, unique=True)

    city: Mapped[str] = mapped_column(String)

    country: Mapped[str] = mapped_column(String)

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer"
    )


# ==========================
# Product
# ==========================

class Product(Base):

    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String)

    category: Mapped[str] = mapped_column(String)

    brand: Mapped[str] = mapped_column(String)

    price: Mapped[float] = mapped_column(Float)

    rating: Mapped[float] = mapped_column(Float)

    stock: Mapped[int] = mapped_column(Integer)

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product"
    )


# ==========================
# Order
# ==========================

class Order(Base):

    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id")
    )

    order_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    payment_method: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(String)

    discount: Mapped[float] = mapped_column(Float, default=0)

    tax: Mapped[float] = mapped_column(Float, default=0)

    shipping: Mapped[float] = mapped_column(Float, default=0)

    total_amount: Mapped[float] = mapped_column(Float)

    net_amount: Mapped[float] = mapped_column(Float)

    customer: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )


# ==========================
# Order Item
# ==========================

class OrderItem(Base):

    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id")
    )

    quantity: Mapped[int] = mapped_column(Integer)

    unit_price: Mapped[float] = mapped_column(Float)

    line_total: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )

    product: Mapped["Product"] = relationship(
        back_populates="order_items"
    )


# ==========================
# Daily Metrics
# ==========================

class DailyMetric(Base):

    __tablename__ = "daily_metrics"

    date: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    revenue: Mapped[float] = mapped_column(Float)

    total_orders: Mapped[int] = mapped_column(Integer)

    total_customers: Mapped[int] = mapped_column(Integer)

    avg_order_value: Mapped[float] = mapped_column(Float)

    total_products_sold: Mapped[int] = mapped_column(Integer)