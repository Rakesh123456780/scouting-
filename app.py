"""
ScoutIQ — Flask REST API  (app.py)
Serves all product / watchlist / alert data from SQLite.
"""
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import json, os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from database import get_connection, init_db

# Load environment variables
load_dotenv()

# ── Configuration ────────────────────────────────────────────────
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "scoutiq_default_secret_key")

def send_otp_email(recipient_email, otp_code, is_reset=False):
    if SENDER_EMAIL == "your-email@gmail.com":
        print(f"\n[WARNING] SENDER_EMAIL not configured in app.py!")
        print(f"To see this OTP actually sent, set up your Gmail and App Password.")
        print(f"Fallback terminal print -> MOCK OTP for {recipient_email}: {otp_code}\n")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"ScoutIQ <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = "ScoutIQ - Password Reset Code" if is_reset else "ScoutIQ - Verify Your Account"

        action_text = "reset your password" if is_reset else "verify your account"
        
        body = f"Hello,\n\nHere is your 6-digit confirmation code to {action_text}:\n\n{otp_code}\n\nThanks,\nThe ScoutIQ Team"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD.replace(" ", ""))
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, recipient_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False

# ── Bootstrap ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)
app.secret_key = FLASK_SECRET_KEY  # Securely sourced from .env

# Initialise DB on first run
init_db()

# ── Activity Logger Helper ───────────────────────────────────────
def log_activity(email, action, details=""):
    try:
        conn = get_connection()
        conn.execute("INSERT INTO activity_logs (user_email, action, details) VALUES (?, ?, ?)", (email, action, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Activity Log Error:", e)

# ── Middleware ───────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_email" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

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
    if "user_email" in session:
        return send_from_directory(BASE_DIR, "index.html")
    return send_from_directory(BASE_DIR, "login.html")


@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return send_from_directory(BASE_DIR, "login.html")
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/profile")
def profile_page():
    if "user_email" not in session:
        return send_from_directory(BASE_DIR, "login.html")
    return send_from_directory(BASE_DIR, "profile.html")

@app.route("/register")
def register_page():
    return send_from_directory(BASE_DIR, "register.html")

@app.route("/forgot-password")
def forgot_password_page():
    return send_from_directory(BASE_DIR, "forgot_password.html")

@app.route("/admin")
def admin_page():
    # Only serve to logged in (or just serve statically for demo purposes)
    return send_from_directory(BASE_DIR, "admin.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


# ══════════════════════════════════════════════════════════════════
#  API  ROUTES
# ══════════════════════════════════════════════════════════════════

# ── Admin Activity API ───────────────────────────────────────────
@app.route("/api/admin/users", methods=["GET"])
@login_required
def get_all_users():
    # In a real app, you would also check for an is_admin flag
    conn = get_connection()
    users = conn.execute("SELECT id, email, is_verified, created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@app.route("/api/admin/activities", methods=["GET"])
@login_required
def get_activities():
    conn = get_connection()
    logs = conn.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

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


# ── Auth ─────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
        
    import random
    otp_code = str(random.randint(100000, 999999))
        
    conn = get_connection()
    try:
        hashed = generate_password_hash(password)
        conn.execute("INSERT INTO users (email, password, otp_code, is_verified) VALUES (?, ?, ?, 0)", (email, hashed, otp_code))
        conn.commit()
        # Send Real Email
        send_otp_email(email, otp_code)
    except sqlite3.IntegrityError:
        existing_user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user and existing_user["is_verified"] == 0:
            conn.execute("UPDATE users SET otp_code = ?, password = ? WHERE email = ?", (otp_code, hashed, email))
            conn.commit()
            # Send Real Email (Resend OTP)
            send_otp_email(email, otp_code)
            conn.close()
            return jsonify({"message": "Check your email for the new OTP.", "requires_otp": True}), 201
            
        conn.close()
        return jsonify({"error": "User already exists"}), 409
    
    conn.close()
    return jsonify({"message": "Registration successful. Please check your email for OTP.", "requires_otp": True}), 201

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email")
    otp_code = data.get("otpCode")
    
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if user and user["otp_code"] == otp_code:
        # Mark verified right away for simplicity here
        conn.execute("UPDATE users SET is_verified = 1, otp_code = NULL WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        # Auto login the session for convenience
        session["user_email"] = email
        log_activity(email, "Verified Email")
        return jsonify({"message": "OTP verified successfully"}), 200
        
    conn.close()
    return jsonify({"error": "Invalid or expired OTP"}), 400

@app.route("/api/login", methods=["POST"])
def login_api():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user["password"], password):
        if user["is_verified"] == 0:
            return jsonify({"error": "Please verify your email using the OTP sent to you.", "unverified": True}), 403
            
        session["user_email"] = email
        log_activity(email, "Logged In")
        return jsonify({"message": "Login successful"}), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    email = session.pop("user_email", None)
    if email:
        log_activity(email, "Logged Out")
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/api/profile", methods=["GET"])
def get_profile():
    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_connection()
    user = conn.execute("SELECT id, email, phone_number, is_verified, created_at FROM users WHERE email = ?", (session["user_email"],)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(dict(user)), 200

@app.route("/api/profile", methods=["PUT"])
def update_profile():
    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    phone_number = data.get("phone_number")
    
    conn = get_connection()
    conn.execute("UPDATE users SET phone_number = ? WHERE email = ?", (phone_number, session["user_email"]))
    conn.commit()
    conn.close()
    
    log_activity(session["user_email"], "Updated Profile")
    return jsonify({"message": "Profile updated successfully"}), 200

@app.route("/api/forgot-password/request-otp", methods=["POST"])
def forgot_password_request_otp():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
        
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if user:
        import random
        otp_code = str(random.randint(100000, 999999))
        conn.execute("UPDATE users SET otp_code = ? WHERE email = ?", (otp_code, email))
        conn.commit()
        
        # Send Real Email for Password Reset
        send_otp_email(email, otp_code, is_reset=True)
        
    conn.close()
    # Always return success to prevent email enumeration
    return jsonify({"message": "If the email exists, an OTP has been sent."}), 200

@app.route("/api/forgot-password/reset", methods=["POST"])
def forgot_password_reset():
    data = request.json
    email = data.get("email")
    otp_code = data.get("otpCode")
    new_password = data.get("newPassword")
    
    if not email or not otp_code or not new_password:
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if user and user["otp_code"] == otp_code:
        hashed = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password = ?, otp_code = NULL WHERE email = ?", (hashed, email))
        conn.commit()
        conn.close()
        return jsonify({"message": "Password reset successfully"}), 200
        
    conn.close()
    return jsonify({"error": "Invalid or expired OTP"}), 400


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
