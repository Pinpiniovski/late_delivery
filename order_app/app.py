from flask import Flask, render_template
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# Informations API Shopify
import os
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOP_NAME = "tammyandbenjamin"
API_VERSION = "2023-10"
BASE_ORDER_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json?fulfillment_status=unfulfilled&limit=250"
PRODUCT_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/{{product_id}}.json"

# En-têtes de la requête
headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def fetch_recent_unfulfilled_orders():
    """
    Récupère les commandes non livrées des 3 derniers mois.
    """
    try:
        # Date il y a 3 mois
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S%z")
        
        # URL avec filtre de date
        url = f"{BASE_ORDER_URL}&created_at_min={three_months_ago}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("orders", [])
        else:
            print(f"Erreur lors de la récupération des commandes: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return []

@app.route("/")
def index():
    # Catégories de commandes
    overdue = []
    next_7_days = []
    next_7_to_15_days = []
    more_than_15_days = []

    orders = fetch_recent_unfulfilled_orders()
    for order in orders:
        order_name = order.get("name")
        order_id = order.get("id")
        order_link = f"https://admin.shopify.com/store/{SHOP_NAME}/orders/{order_id}"
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
                    order_data = {
                        "order_name": order_name,
                        "order_link": order_link,
                        "quantity": quantity
                    }
                    if days_left < 0:
                        overdue.append(order_data)
                    elif 0 <= days_left <= 7:
                        next_7_days.append(order_data)
                    elif 8 <= days_left <= 15:
                        next_7_to_15_days.append(order_data)
                    elif days_left > 15:
                        more_than_15_days.append(order_data)
                    break

    return render_template(
        "orders_grouped.html",
        overdue=overdue,
        next_7_days=next_7_days,
        next_7_to_15_days=next_7_to_15_days,
        more_than_15_days=more_than_15_days,
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
