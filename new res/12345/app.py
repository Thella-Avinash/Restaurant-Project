
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, g
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'conzura_restaurant_secret_2024'

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "restaurant.db"
)


# ---------------- DATABASE ----------------

def get_db():

    if "db" not in g:

        g.db = sqlite3.connect(
            DATABASE
        )

        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(error):

    db = g.pop(
        "db",
        None
    )

    if db:

        db.close()

def init_db():

    db = sqlite3.connect(
        DATABASE
    )

    db.row_factory = sqlite3.Row


    # ADD NEW ORDER COLUMNS

    try:

        db.execute(
            """
            ALTER TABLE orders
            ADD COLUMN customer_phone TEXT
            """
        )

    except:

        pass


    try:

        db.execute(
            """
            ALTER TABLE orders
            ADD COLUMN customer_email TEXT
            """
        )

    except:

        pass


    db.executescript(
        """


CREATE TABLE IF NOT EXISTS customers(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT NOT NULL,

phone TEXT,

email TEXT,

address TEXT,

points INTEGER DEFAULT 0

);

CREATE TABLE IF NOT EXISTS users(

id INTEGER PRIMARY KEY AUTOINCREMENT,

username TEXT UNIQUE,

password TEXT,

role TEXT

);


CREATE TABLE IF NOT EXISTS menu_items(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

category TEXT,

price REAL,

description TEXT,

image TEXT,

available INTEGER DEFAULT 1

);




CREATE TABLE IF NOT EXISTS orders (

id INTEGER PRIMARY KEY AUTOINCREMENT,

table_number INTEGER NOT NULL,

customer_name TEXT,

customer_phone TEXT,

customer_email TEXT,

loyalty_points INTEGER DEFAULT 0,

status TEXT DEFAULT 'pending',

created_by INTEGER,

created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

updated_at DATETIME DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS bills(

id INTEGER PRIMARY KEY AUTOINCREMENT,

total_amount REAL,

created_at DATETIME DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS inventory(

id INTEGER PRIMARY KEY AUTOINCREMENT,

quantity REAL,

min_quantity REAL

);

        """
    )

    db.commit()

    db.close()


# ---------------- IMPORT MODULES ----------------

from modules.auth import auth_bp
from modules.menu import menu_bp
from modules.orders import orders_bp
from modules.billing import billing_bp
from modules.inventory import inventory_bp
from modules.reports import reports_bp


# CUSTOMER MODULE
from modules.customers.routes import customers_bp


# ---------------- REGISTER ----------------

app.register_blueprint(
    auth_bp,
    url_prefix="/auth"
)

app.register_blueprint(
    menu_bp,
    url_prefix="/menu"
)

app.register_blueprint(
    orders_bp,
    url_prefix="/orders"
)

app.register_blueprint(
    billing_bp,
    url_prefix="/billing"
)

app.register_blueprint(
    inventory_bp,
    url_prefix="/inventory"
)

app.register_blueprint(
    reports_bp,
    url_prefix="/reports"
)

app.register_blueprint(
    customers_bp,
    url_prefix="/customers"
)


# ---------------- ROUTES ----------------

@app.route("/")
def index():

    if "user" not in session:

        return redirect(
            url_for(
                "auth.login"
            )
        )

    return redirect(
        "/dashboard"
    )


@app.route('/api/dashboard-stats')
def dashboard_stats():

    db = get_db()

    revenue_data = db.execute(
        """

        SELECT

        DATE(
        created_at
        ) date,

        COALESCE(
        SUM(
        total_amount
        ),
        0
        ) revenue

        FROM bills

        WHERE

        DATE(created_at)

        >=

        DATE(
        'now',
        '-6 day'
        )

        GROUP BY

        DATE(created_at)

        ORDER BY

        DATE(created_at)

        """
    ).fetchall()


    return jsonify(

        {

        "labels":[

        str(
        r["date"]
        )

        for r in revenue_data

        ],

        "values":[

        float(
        r["revenue"]
        )

        for r in revenue_data

        ]

        }

    )



     

@app.route(
"/api/dashboard"
)
def api_dashboard():

    return jsonify(

        {

            "status":

            "ok"

        }

    )


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:

        return redirect(
            url_for(
                'auth.login'
            )
        )

    db = get_db()

    stats = {}

    # Revenue
    stats["today_revenue"] = db.execute(
        """
        SELECT
        COALESCE(
        SUM(total_amount),
        0
        )
        FROM bills
        """
    ).fetchone()[0]


    # Orders
    stats["total_orders"] = db.execute(
        """
        SELECT COUNT(*)
        FROM orders
        """
    ).fetchone()[0]


    # Menu
    stats["menu_items"] = db.execute(
        """
        SELECT COUNT(*)
        FROM menu_items
        """
    ).fetchone()[0]


    # Inventory
    stats["low_stock"] = db.execute(
        """
        SELECT COUNT(*)
        FROM inventory
        WHERE quantity<=min_quantity
        """
    ).fetchone()[0]


    # Pending
    stats["pending_orders"] = db.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE status='pending'
        """
    ).fetchone()[0]


    # Recent Orders
    stats["recent_orders"] = db.execute(
        """
        SELECT

        id,

        table_number,

        status,

        customer_name,

        created_at,

        0 AS amount

        FROM orders

        ORDER BY id DESC

        LIMIT 5
        """
    ).fetchall()


    # CUSTOMER ANALYTICS

    stats["total_customers"] = db.execute(
        """
        SELECT COUNT(*)
        FROM customers
        """
    ).fetchone()[0]


    stats["new_customers"] = db.execute(
        """
        SELECT COUNT(*)
        FROM customers
        """
    ).fetchone()[0]


    stats["returning_customers"] = db.execute(
        """
        SELECT COUNT(*)

        FROM (

            SELECT customer_phone

            FROM orders

            GROUP BY customer_phone

            HAVING COUNT(*) > 1

        )
        """
    ).fetchone()[0]


    top = db.execute(
        """
        SELECT

        customer_name,

        COUNT(*) total

        FROM orders

        WHERE customer_name!=''

        GROUP BY customer_name

        ORDER BY total DESC

        LIMIT 1
        """
    ).fetchone()


    stats["top_customer"] = (

        top["customer_name"]

        if top

        else "No Customer"

    )


    return render_template(

        "dashboard.html",

        stats=stats,

        user=session["user"]

    )



# ---------------- RUN ----------------

if __name__ == "__main__":

    init_db()

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )
