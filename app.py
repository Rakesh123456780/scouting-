"""
ScoutIQ — Flask REST API  (app.py)
Serves all product / watchlist / alert data from SQLite.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os
import sqlite3
from dotenv import load_dotenv
from database import get_connection, init_db

# Load environment variables
load_dotenv()

# ── Bootstrap ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)

# Initialise DB on first run
init_db()


def row_to_dict(row):
    """Convert a sqlite3.Row to a plain dict and parse JSON columns."""
    d = dict(row)
    if "tags" in d and isinstance(d["tags"], str):
        try:
            d["tags"] = json.loads(d["tags"])
        except json.JSONDecodeError:
            d["tags"] = []
    # Rename snake_case → camelCase for JS consumption
    mapping = {
        "original_price": "originalPrice",
        "type_name": "typeName",
        "created_at": "createdAt",
        "product_id": "productId",
        "added_at": "addedAt",
    }
    for old, new in mapping.items():
        if old in d:
            d[new] = d.pop(old)
    return d


# ── Static file serving ─────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory(BASE_DIR, "index.html")



@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


# ══════════════════════════════════════════════════════════════════
#  API  ROUTES
# ══════════════════════════════════════════════════════════════════



# ── Products ─────────────────────────────────────────────────────
@app.route("/api/products", methods=["GET"])
def get_products():
    """Return all products. Optional query params: category, sort, minScore, q"""
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    # Category filter
    category = request.args.get("category")
    if category:
        query += " AND category = ?"
        params.append(category)

    # Min score filter
    min_score = request.args.get("minScore")
    if min_score:
        query += " AND score >= ?"
        params.append(int(min_score))

    # Text search
    q = request.args.get("q")
    if q:
        query += " AND (LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(brand) LIKE ?)"
        like = f"%{q.lower()}%"
        params.extend([like, like, like])

    # Sorting
    sort = request.args.get("sort", "trending")
    sort_map = {
        "trending": "score DESC",
        "price-low": "price ASC",
        "price-high": "price DESC",
        "rating": "rating DESC",
        "newest": "id DESC",
    }
    query += f" ORDER BY {sort_map.get(sort, 'score DESC')}"

    cur.execute(query, params)
    products = [row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(products)





@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(row_to_dict(row))


@app.route("/api/products", methods=["POST"])
def add_product():
    """Add a new product."""
    data = request.json
    conn = get_connection()
    conn.execute(
        """INSERT INTO products (name, category, price, original_price, emoji, rating, reviews, score, tags, sales, margin, demand, description, brand)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"], data["category"], data["price"],
            data.get("originalPrice"), data.get("emoji", "📦"),
            data.get("rating", 0), data.get("reviews", 0),
            data.get("score", 50), json.dumps(data.get("tags", [])),
            data.get("sales", 0), data.get("margin", 0),
            data.get("demand", "Medium"), data.get("description", ""),
            data.get("brand", ""),
        ),
    )
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return jsonify({"id": new_id, "message": "Product created"}), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Update an existing product."""
    data = request.json
    conn = get_connection()
    conn.execute(
        """UPDATE products SET name=?, category=?, price=?, original_price=?,
           emoji=?, rating=?, reviews=?, score=?, tags=?, sales=?, margin=?,
           demand=?, description=?, brand=?
           WHERE id=?""",
        (
            data["name"], data["category"], data["price"],
            data.get("originalPrice"), data.get("emoji"),
            data.get("rating"), data.get("reviews"),
            data.get("score"), json.dumps(data.get("tags", [])),
            data.get("sales"), data.get("margin"),
            data.get("demand"), data.get("description"),
            data.get("brand"), product_id,
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Product updated"})


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted"})


# ── Watchlist ────────────────────────────────────────────────────
@app.route("/api/watchlist", methods=["GET"])
def get_watchlist():
    """Return list of product IDs in the watchlist."""
    conn = get_connection()
    rows = conn.execute("SELECT product_id FROM watchlist").fetchall()
    conn.close()
    return jsonify([r["product_id"] for r in rows])


@app.route("/api/watchlist/<int:product_id>", methods=["POST"])
def add_to_watchlist(product_id):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO watchlist (product_id) VALUES (?)", (product_id,))
        conn.commit()
    except Exception:
        conn.close()
        return jsonify({"message": "Already in watchlist"}), 409
    conn.close()
    return jsonify({"message": "Added to watchlist"}), 201


@app.route("/api/watchlist/<int:product_id>", methods=["DELETE"])
def remove_from_watchlist(product_id):
    conn = get_connection()
    conn.execute("DELETE FROM watchlist WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Removed from watchlist"})


# ── Alerts ───────────────────────────────────────────────────────
@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/api/alerts", methods=["POST"])
def create_alert():
    data = request.json
    icons = {"price-drop": "📉", "price-rise": "📈", "trend": "🔥", "stock": "📦"}
    names = {"price-drop": "Price Drop", "price-rise": "Price Rise", "trend": "Trend Alert", "stock": "Stock Alert"}
    conn = get_connection()
    conn.execute(
        "INSERT INTO alerts (product, type, type_name, description, status, icon) VALUES (?, ?, ?, ?, 'active', ?)",
        (
            data["product"], data["type"],
            names.get(data["type"], data["type"]),
            data.get("description", ""),
            icons.get(data["type"], "🔔"),
        ),
    )
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return jsonify({"id": new_id, "message": "Alert created"}), 201


@app.route("/api/alerts/<int:alert_id>", methods=["PATCH"])
def update_alert_status(alert_id):
    """Toggle or set alert status."""
    data = request.json
    conn = get_connection()
    if "status" in data:
        conn.execute("UPDATE alerts SET status = ? WHERE id = ?", (data["status"], alert_id))
    else:
        # Toggle active <-> paused
        row = conn.execute("SELECT status FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        if row:
            new_status = "paused" if row["status"] != "paused" else "active"
            conn.execute("UPDATE alerts SET status = ? WHERE id = ?", (new_status, alert_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Alert updated"})


@app.route("/api/alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(alert_id):
    conn = get_connection()
    conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Alert deleted"})


# ── Categories ───────────────────────────────────────────────────
@app.route("/api/categories", methods=["GET"])
def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY pct DESC").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


# ── Geo Demand ───────────────────────────────────────────────────
@app.route("/api/geo", methods=["GET"])
def get_geo():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM geo_demand ORDER BY pct DESC").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


# ── Brands ───────────────────────────────────────────────────────
@app.route("/api/brands", methods=["GET"])
def get_brands():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM brands ORDER BY score DESC").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


# ── Insights ─────────────────────────────────────────────────────
@app.route("/api/insights", methods=["GET"])
def get_insights():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM insights").fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


# ── Dashboard summary ───────────────────────────────────────────
@app.route("/api/dashboard", methods=["GET"])
def dashboard_summary():
    """Return KPI values from the database."""
    conn = get_connection()
    cur = conn.cursor()
    total_products = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    watchlist_count = cur.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    market_opp = cur.execute("SELECT SUM(price * sales) / 1000000.0 FROM products").fetchone()[0] or 0
    trending = cur.execute("SELECT COUNT(*) FROM products WHERE tags LIKE '%trending%'").fetchone()[0]
    conn.close()
    return jsonify({
        "totalProducts": total_products,
        "watchlistCount": watchlist_count,
        "marketOpportunity": round(market_opp, 1),
        "trending": trending,
    })


# ═════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import threading
    import webbrowser
    print("[*] ScoutIQ API running at http://127.0.0.1:5000")
    # Only open browser once, not on reloader spawns
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.25, lambda: webbrowser.open("http://127.0.0.1:5000/")).start()
    app.run(debug=True, port=5000)
