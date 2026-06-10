# modules/customers/routes.py
from flask import Blueprint, render_template, request, redirect, session

from .models import (
    get_customers,
    add_customer,
    search_customer,
    get_customer_stats
)

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/")
def customer_list():
    search = request.args.get("q", "")
    customers = search_customer(search) if search else get_customers()
    stats = get_customer_stats()
    return render_template(
        "customers/customer_list.html",
        customers=customers,
        stats=stats,
        user=session.get("user")
    )


@customers_bp.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        add_customer(
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["address"]
        )
        return redirect("/customers")
    return render_template("customers/add_customer.html")
