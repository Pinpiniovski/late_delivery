from flask import Flask, render_template
from tasks import cached_orders
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

@app.route("/")
def index():
    # Catégories de commandes
    overdue = defaultdict(list)
    next_7_days = defaultdict(list)
    next_7_to_15_days = defaultdict(list)
    more_than_15_days = defaultdict(list)

    today = datetime.now()

    for order in cached_orders:
        order_name = order.get("name")
        order_id = order.get("id")
        order_link = f"https://admin.shopify.com/store/tammyandbenjamin/orders/{order_id}"
        created_at = datetime.strptime(order.get("created_at"), "%Y-%m-%dT%H:%M:%S%z")
        end_delivery_date = created_at + timedelta(days=24)
        days_left = (end_delivery_date - today).days

        for item in order.get("line_items", []):
            product_title = item.get("title", "Unknown Product")
            quantity = item.get("quantity", 1)

            if days_left < 0:
                overdue[product_title].append({"order_name": order_name, "order_link": order_link, "quantity": quantity})
            elif 0 <= days_left <= 7:
                next_7_days[product_title].append({"order_name": order_name, "order_link": order_link, "quantity": quantity})
            elif 8 <= days_left <= 15:
                next_7_to_15_days[product_title].append({"order_name": order_name, "order_link": order_link, "quantity": quantity})
            elif days_left > 15:
                more_than_15_days[product_title].append({"order_name": order_name, "order_link": order_link, "quantity": quantity})

    return render_template(
        "orders_grouped.html",
        overdue=overdue,
        next_7_days=next_7_days,
        next_7_to_15_days=next_7_to_15_days,
        more_than_15_days=more_than_15_days,
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
