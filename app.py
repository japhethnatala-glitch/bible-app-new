import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------------
# Database initialization
# ---------------------------
def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Verses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book TEXT,
        chapter INTEGER,
        verse INTEGER,
        text TEXT,
        translation TEXT
    )
    """)

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        credits INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# Helper: Add credits to user
# ---------------------------
def add_credits(email, credits):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET credits = credits + ? WHERE email = ?", (credits, email))
    conn.commit()
    conn.close()

# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        flash("Registration successful!", "success")
    except sqlite3.IntegrityError:
        flash("Email already registered.", "danger")
    conn.close()

    return redirect(url_for("index"))

@app.route("/balance/<email>")
def balance(email):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT credits FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row:
        return jsonify({"email": email, "credits": row[0]})
    else:
        return jsonify({"error": "User not found"}), 404

# ---------------------------
# NOWPayments Webhook
# ---------------------------
@app.route("/nowpayments-webhook", methods=["POST"])
def nowpayments_webhook():
    data = request.json
    payment_status = data.get("payment_status")
    order_id = data.get("order_id")   # e.g. CREDITS100, CREDITS250, CREDITS600
    customer_email = data.get("customer_email")  # optional if you collect it

    if payment_status == "finished" and customer_email:
        if order_id == "CREDITS100":
            add_credits(customer_email, 100)
        elif order_id == "CREDITS250":
            add_credits(customer_email, 250)
        elif order_id == "CREDITS600":
            add_credits(customer_email, 600)
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "ignored"}), 200

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
