from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("/app/orders_cache.db")
    cursor = conn.cursor()

    cursor.execute("SELECT product_title, order_name, order_link, quantity FROM orders WHERE category='overdue'")
    overdue = cursor.fetchall()

    cursor.execute("SELECT product_title, order_name, order_link, quantity FROM orders WHERE category='next_7_days'")
    next_7_days = cursor.fetchall()

    cursor.execute("SELECT product_title, order_name, order_link, quantity FROM orders WHERE category='next_7_to_15_days'")
    next_7_to_15_days = cursor.fetchall()

    cursor.execute("SELECT product_title, order_name, order_link, quantity FROM orders WHERE category='more_than_15_days'")
    more_than_15_days = cursor.fetchall()

    conn.close()

    return render_template(
        "orders_grouped.html",
        overdue=overdue,
        next_7_days=next_7_days,
        next_7_to_15_days=next_7_to_15_days,
        more_than_15_days=more_than_15_days,
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
