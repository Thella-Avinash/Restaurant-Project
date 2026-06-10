
# modules/customers/models.py

import sqlite3
import os


DATABASE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    ),
    "restaurant.db"
)


def connect_db():

    db = sqlite3.connect(
        DATABASE
    )

    db.row_factory = sqlite3.Row

    return db


def get_customers():

    db = connect_db()

    data = db.execute(
        """
        SELECT *
        FROM customers
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return data


def add_customer(
    name,
    phone,
    email,
    address
):

    db = connect_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS customers(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            phone TEXT,

            email TEXT,

            address TEXT,

            points INTEGER DEFAULT 0

        )
        """
    )

    db.execute(
        """
        INSERT INTO customers
        (
            name,
            phone,
            email,
            address
        )

        VALUES

        (
            ?,
            ?,
            ?,
            ?
        )
        """,

        (
            name,
            phone,
            email,
            address
        )

    )

    db.commit()

    db.close()


def search_customer(search):

    db = connect_db()

    data = db.execute(
        """
        SELECT *
        FROM customers

        WHERE

        name LIKE ?

        OR phone LIKE ?

        OR email LIKE ?
        """,

        (
            f"%{search}%",

            f"%{search}%",

            f"%{search}%"
        )
    ).fetchall()

    db.close()

    return data


def get_customer_stats():

    db = connect_db()

    total = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]

    new = db.execute("SELECT COUNT(*) FROM customers").fetchone()[0]

    returning = db.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT customer_phone
            FROM orders
            WHERE customer_phone != ''
            GROUP BY customer_phone
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    top = db.execute(
        """
        SELECT name FROM customers c
        JOIN (
            SELECT customer_phone, COUNT(*) as cnt
            FROM orders
            WHERE customer_phone != ''
            GROUP BY customer_phone
            ORDER BY cnt DESC
            LIMIT 1
        ) o ON c.phone = o.customer_phone
        """
    ).fetchone()

    db.close()

    return {
        "total": total,
        "new": new,
        "returning": returning,
        "top": top[0] if top else "—"
    }

