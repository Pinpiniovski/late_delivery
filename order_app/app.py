from flask import Flask, render_template
import requests
from datetime import datetime, timedelta  # Pour manipuler les dates
from collections import defaultdict  # Pour grouper les commandes par produit

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

@app.route("/")
def index():
    # Catégories de commandes
    overdue = defaultdict(list)
    next_7_days = defaultdict(list)
    next_7_to_15_days = defaultdict(list)
    more_than_15_days = defaultdict(list)

    # Récupérer toutes les commandes non traitées
    response = requests.get(BASE_ORDER_URL, headers=headers)
    if response.status_code == 200:
        orders = response.json().get("orders", [])
        
        for order in orders:
            # Exclure les commandes annulées ou expirées
            if order.get("cancelled_at") or order.get("financial_status") == "expired":
                continue

            order_name = order.get("name")
            order_id = order.get("id")
            order_link = f"https://admin.shopify.com/store/{SHOP_NAME}/orders/{order_id}"
            created_at = datetime.strptime(order.get("created_at"), "%Y-%m-%dT%H:%M:%S%z")
            end_delivery_date = created_at + timedelta(days=24)
            today = datetime.now(created_at.tzinfo)
            days_left = (end_delivery_date - today).days

            for item in order.get("line_items", []):
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)  # Quantité commandée

                # Vérifier les tags du produit
                product_response = requests.get(PRODUCT_URL.format(product_id=product_id), headers=headers)
                if product_response.status_code == 200:
                    product_data = product_response.json().get("product", {})
                    product_tags = product_data.get("tags", "")
                    product_title = product_data.get("title", "Unknown Product")

                    # Si le produit contient le tag "late_delivery", classifier la commande
                    if "late_delivery" in product_tags.split(", "):
                        order_data = {
                            "order_name": order_name,
                            "order_link": order_link,
                            "quantity": quantity
                        }
                        if days_left < 0:
                            overdue[product_title].append(order_data)
                        elif 0 <= days_left <= 7:
                            next_7_days[product_title].append(order_data)
                        elif 8 <= days_left <= 15:
                            next_7_to_15_days[product_title].append(order_data)
                        elif days_left > 15:
                            more_than_15_days[product_title].append(order_data)
                        break  # Passer à la commande suivante dès qu'un produit correspond

    # Rendre les résultats dans une page HTML
    return render_template(
        "orders_grouped.html",
        overdue=overdue,
        next_7_days=next_7_days,
        next_7_to_15_days=next_7_to_15_days,
        more_than_15_days=more_than_15_days,
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
