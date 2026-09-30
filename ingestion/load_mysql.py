from pathlib import Path

import mysql.connector
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

DB_CONFIG = {
    "host": "localhost",
    "user": "ecommerce_app",
    "password": "EcommerceDev2026!",
    "database": "ecommerce",
}


TABLES = {
    "customers": DATA_DIR / "customers.csv",
    "products": DATA_DIR / "products.csv",
    "orders": DATA_DIR / "orders.csv",
    "order_items": DATA_DIR / "order_items.csv",
    "payments": DATA_DIR / "payments.csv",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def load_table(connection, table_name, csv_path):
    print(f"Loading {table_name}...")

    dataframe = pd.read_csv(csv_path)

    # Convert NaN values to None so MySQL receives NULL.
    dataframe = dataframe.astype(object).where(
        pd.notna(dataframe),
        None,
    )

    columns = list(dataframe.columns)

    column_names = ", ".join(f"`{column}`" for column in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = f"""
        INSERT INTO `{table_name}`
        ({column_names})
        VALUES ({placeholders})
    """

    cursor = connection.cursor()

    rows = [
        tuple(row)
        for row in dataframe.itertuples(index=False, name=None)
    ]

    cursor.executemany(query, rows)
    connection.commit()

    cursor.close()

    print(f"  Loaded {len(rows):,} rows")


def main():
    connection = get_connection()

    try:
        for table_name, csv_path in TABLES.items():
            load_table(
                connection,
                table_name,
                csv_path,
            )

    finally:
        connection.close()

    print("\nMySQL ingestion completed successfully.")


if __name__ == "__main__":
    main()
