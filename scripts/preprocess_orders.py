import sqlite3
import requests
from datetime import datetime, timedelta
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOP_NAME = "tammyandbenjamin"
API_VERSION = "2023-10"
BASE_ORDER_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json?fulfillment_status=unfulfilled&limit=250"
PRODUCT_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{{product_id}}.json"
headers = {"X-Shopify-Access-Token": ACCESS_TOKEN}

conn = sqlite3.connect("/app/orders_cache.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_name TEXT,
    order_link TEXT,
    product_title TEXT,
    quantity INTEGER,
    category TEXT
)
""")

def fetch_orders():
    response = requests.get(BASE_ORDER_URL, headers=headers)
    if response.status_code != 200:
        return []

    orders = response.json().get("orders", [])
    results = []
    for order in orders:
        if order.get("cancelled_at") or order.get("financial_status") == "expired":
            continue

        created_at = datetime.strptime(order.get("created_at"), "%Y-%m-%dT%H:%M:%S%z")
        end_delivery_date = created_at + timedelta(days=24)
        today = datetime.now(created_at.tzinfo)
        days_left = (end_delivery_date - today).days

        for item in order.get("line_items", []):
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            product_response = requests.get(PRODUCT_URL.format(product_id=product_id), headers=headers)
            if product_response.status_code == 200:
                product_data = product_response.json().get("product", {})
                product_tags = product_data.get("tags", "")
                product_title = product_data.get("title", "Unknown Product")

                if "late_delivery" in product_tags.split(", "):
                    category = (
                        "overdue" if days_left < 0 else
                        "next_7_days" if 0 <= days_left <= 7 else
                        "next_7_to_15_days" if 8 <= days_left <= 15 else
                        "more_than_15_days"
                    )
                    results.append((order.get("name"), 
                                    f"https://admin.shopify.com/store/{SHOP_NAME}/orders/{order.get('id')}",
                                    product_title, 
                                    quantity, 
                                    category))
    return results

orders = fetch_orders()
cursor.executemany("INSERT INTO orders (order_name, order_link, product_title, quantity, category) VALUES (?, ?, ?, ?, ?)", orders)
conn.commit()
conn.close()
