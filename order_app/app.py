from flask import Flask, render_template
import requests
import asyncio
import aiohttp
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

# Cache pour éviter les appels répétés à l'API des produits
product_cache = {}

async def fetch_product(session, product_id):
    if product_id not in product_cache:
        async with session.get(PRODUCT_URL.format(product_id=product_id), headers=headers) as response:
            if response.status == 200:
                product_data = await response.json()
                product_cache[product_id] = product_data.get("product", {})
            else:
                product_cache[product_id] = {}  # Stocker une valeur vide en cas d'échec
    return product_cache[product_id]

async def fetch_all_products(product_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_product(session, product_id) for product_id in product_ids]
        await asyncio.gather(*tasks)

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

        # Filtrer les commandes annulées ou expirées
        orders = [
            order for order in orders
            if not order.get("cancelled_at") and order.get("financial_status") != "expired"
        ]

        # Récupérer les IDs des produits pour un préchargement
        product_ids = {item["product_id"] for order in orders for item in order["line_items"]}
        asyncio.run(fetch_all_products(product_ids))

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
                quantity = item.get("quantity", 1)  # Quantité commandée

                # Utiliser les données du cache
                product_data = product_cache.get(product_id, {})
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
    app.run(debug=True, host='0.0.0.0', port=5001)
