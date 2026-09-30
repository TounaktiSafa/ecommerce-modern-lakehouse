from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


SEED = 42
fake = Faker()
fake.seed_instance(SEED)
np.random.seed(SEED)

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

N_CUSTOMERS = 10_000
N_PRODUCTS = 1_000
N_ORDERS = 50_000
N_ORDER_ITEMS = 120_000
N_PAYMENTS = 50_000


# ---------------------------------------------------------
# Customers
# ---------------------------------------------------------

def generate_customers() -> pd.DataFrame:
    customers = []

    countries = [
        "Tunisia",
        "France",
        "Germany",
        "United Kingdom",
        "Italy",
        "Spain",
        "Canada",
        "United States",
    ]

    for customer_id in range(1, N_CUSTOMERS + 1):
        customers.append(
            {
                "customer_id": customer_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "country": np.random.choice(countries),
                "signup_date": fake.date_between(
                    start_date="-3y",
                    end_date="today",
                ),
            }
        )

    return pd.DataFrame(customers)


# ---------------------------------------------------------
# Products
# ---------------------------------------------------------

def generate_products() -> pd.DataFrame:
    categories = [
        "Electronics",
        "Home",
        "Fashion",
        "Sports",
        "Books",
        "Beauty",
        "Toys",
    ]

    products = []

    for product_id in range(1, N_PRODUCTS + 1):
        products.append(
            {
                "product_id": product_id,
                "product_name": fake.catch_phrase(),
                "category": np.random.choice(categories),
                "price": round(np.random.uniform(5, 2000), 2),
                "stock_quantity": np.random.randint(0, 500),
            }
        )

    return pd.DataFrame(products)


# ---------------------------------------------------------
# Orders
# ---------------------------------------------------------

def generate_orders() -> pd.DataFrame:
    statuses = [
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled",
    ]

    orders = []

    for order_id in range(1, N_ORDERS + 1):
        orders.append(
            {
                "order_id": order_id,
                "customer_id": np.random.randint(1, N_CUSTOMERS + 1),
                "order_date": fake.date_time_between(
                    start_date="-2y",
                    end_date="now",
                ),
                "status": np.random.choice(
                    statuses,
                    p=[0.08, 0.15, 0.20, 0.50, 0.07],
                ),
                "total_amount": round(
                    np.random.uniform(10, 5000),
                    2,
                ),
            }
        )

    return pd.DataFrame(orders)


# ---------------------------------------------------------
# Order Items
# ---------------------------------------------------------

def generate_order_items() -> pd.DataFrame:
    items = []

    for item_id in range(1, N_ORDER_ITEMS + 1):
        items.append(
            {
                "order_item_id": item_id,
                "order_id": np.random.randint(1, N_ORDERS + 1),
                "product_id": np.random.randint(1, N_PRODUCTS + 1),
                "quantity": np.random.randint(1, 6),
                "unit_price": round(
                    np.random.uniform(5, 2000),
                    2,
                ),
            }
        )

    return pd.DataFrame(items)


# ---------------------------------------------------------
# Payments
# ---------------------------------------------------------

def generate_payments() -> pd.DataFrame:
    methods = [
        "credit_card",
        "debit_card",
        "paypal",
        "bank_transfer",
    ]

    statuses = [
        "pending",
        "completed",
        "failed",
        "refunded",
    ]

    payments = []

    for payment_id in range(1, N_PAYMENTS + 1):
        payments.append(
            {
                "payment_id": payment_id,
                "order_id": np.random.randint(1, N_ORDERS + 1),
                "payment_date": fake.date_time_between(
                    start_date="-2y",
                    end_date="now",
                ),
                "payment_method": np.random.choice(methods),
                "amount": round(
                    np.random.uniform(10, 5000),
                    2,
                ),
                "status": np.random.choice(
                    statuses,
                    p=[0.05, 0.80, 0.10, 0.05],
                ),
            }
        )

    return pd.DataFrame(payments)


# ---------------------------------------------------------
# Inject controlled data-quality issues
# ---------------------------------------------------------

def inject_data_quality_issues(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
):
    # Customers
    customers.loc[10, "email"] = None
    customers.loc[20, "email"] = "invalid-email"
    customers.loc[30, "signup_date"] = pd.Timestamp("2030-01-01")

    # Duplicate customer
    customers.loc[40] = customers.loc[41]

    # Products
    products.loc[10, "price"] = -50
    products.loc[20, "stock_quantity"] = -10
    products.loc[30, "category"] = None

    # Duplicate product
    products.loc[40] = products.loc[41]

    # Orders
    orders.loc[10, "customer_id"] = 999999
    orders.loc[20, "total_amount"] = -100
    orders.loc[30, "status"] = "unknown_status"
    orders.loc[40, "order_date"] = pd.Timestamp("2035-01-01")

    # Duplicate order
    orders.loc[50] = orders.loc[51]

    # Order items
    order_items.loc[10, "quantity"] = -2
    order_items.loc[20, "quantity"] = 0
    order_items.loc[30, "product_id"] = 999999
    order_items.loc[40, "order_id"] = 999999

    # Payments
    payments.loc[10, "amount"] = -250
    payments.loc[20, "order_id"] = 999999
    payments.loc[30, "status"] = "invalid_status"

    return (
        customers,
        products,
        orders,
        order_items,
        payments,
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print("Generating e-commerce datasets...")

    customers = generate_customers()
    products = generate_products()
    orders = generate_orders()
    order_items = generate_order_items()
    payments = generate_payments()

    (
        customers,
        products,
        orders,
        order_items,
        payments,
    ) = inject_data_quality_issues(
        customers,
        products,
        orders,
        order_items,
        payments,
    )

    datasets = {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
    }

    for name, dataframe in datasets.items():
        output_path = OUTPUT_DIR / f"{name}.csv"
        dataframe.to_csv(output_path, index=False)

        print(
            f"{name}: {len(dataframe):,} rows "
            f"→ {output_path}"
        )

    print("\nData generation completed successfully.")


if __name__ == "__main__":
    main()
