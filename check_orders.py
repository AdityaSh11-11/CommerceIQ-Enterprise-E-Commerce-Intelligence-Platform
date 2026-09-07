from database import engine
import pandas as pd


df = pd.read_sql(
    """
    SELECT *
    FROM orders
    ORDER BY order_id DESC
    LIMIT 10
    """,
    engine
)


print(df)

print("\nTotal Orders:")
print(len(pd.read_sql("SELECT * FROM orders", engine)))