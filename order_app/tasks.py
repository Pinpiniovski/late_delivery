from celery import Celery
import requests
import os
from datetime import datetime

# Configuration de Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SHOP_NAME = "tammyandbenjamin"
API_VERSION = "2023-10"
BASE_ORDER_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json?fulfillment_status=unfulfilled&limit=250"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# Variable pour stocker les données en cache
cached_orders = []

@celery_app.task
def fetch_all_unfulfilled_orders():
    """Récupère toutes les commandes non traitées."""
    global cached_orders
    response = requests.get(BASE_ORDER_URL, headers=headers)
    if response.status_code == 200:
        orders = response.json().get("orders", [])
        cached_orders = orders  # Remplacer les anciennes données
        print(f"[{datetime.now()}] Toutes les commandes unfulfilled récupérées.")
    else:
        print(f"[{datetime.now()}] Erreur : {response.status_code}")

@celery_app.task
def fetch_recent_unfulfilled_orders():
    """Récupère uniquement les commandes récentes."""
    global cached_orders
    response = requests.get(BASE_ORDER_URL, headers=headers)
    if response.status_code == 200:
        orders = response.json().get("orders", [])
        new_orders = [order for order in orders if datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S%z") > datetime.now().replace(hour=0, minute=0, second=0)]
        cached_orders.extend(new_orders)  # Ajouter les nouvelles commandes
        print(f"[{datetime.now()}] Commandes récentes récupérées.")
    else:
        print(f"[{datetime.now()}] Erreur : {response.status_code}")
