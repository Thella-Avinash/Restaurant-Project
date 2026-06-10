from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from modules.database import get_db

billing_bp = Blueprint('billing', __name__)
TAX_RATE = 0.05  # 5% GST

@billing_bp.route('/')
def index():

    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if session['user']['role'] == 'admin':
        flash(
            'Access denied. Admin can only manage the Menu.',
            'error'
        )
        return redirect(
            url_for('menu.index')
        )

    db = get_db()

    bills = db.execute(
        """
        SELECT
            b.*,
            o.table_number,
            o.customer_name
        FROM bills b
        JOIN orders o
        ON b.order_id=o.id
        ORDER BY b.created_at DESC
        """
    ).fetchall()


    # DASHBOARD VALUES

    today_revenue = sum(
        float(
            bill['total_amount'] or 0
        )
        for bill in bills
    )


    total_bills = len(
        bills
    )


    avg_bill = (

        today_revenue
        /
        total_bills

        if total_bills

        else 0

    )


    payments = len([
        bill
        for bill in bills
        if bill['payment_method']
    ])


    return render_template(

        'billing.html',

        bills=bills,

        today_revenue=today_revenue,

        total_bills=total_bills,

        avg_bill=avg_bill,

        payments=payments,

        user=session['user']

    )

@billing_bp.route('/generate/<int:order_id>', methods=['GET', 'POST'])
def generate(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()

    # Check if bill already exists
    existing = db.execute("SELECT id FROM bills WHERE order_id=?", (order_id,)).fetchone()
    if existing:
        flash('Bill already generated for this order!', 'warning')
        return redirect(url_for('billing.receipt', order_id=order_id))

    # Check order exists and has items
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('orders.index'))

    items = db.execute(
        "SELECT oi.quantity, oi.unit_price FROM order_items oi WHERE oi.order_id=?", (order_id,)
    ).fetchall()

    if not items:
        flash('Cannot generate bill: order has no items!', 'error')
        return redirect(url_for('orders.index'))

    subtotal = sum(float(i['quantity']) * float(i['unit_price']) for i in items)
    try:
        discount = float(request.form.get('discount', 0) or 0)
    except (ValueError, TypeError):
        discount = 0.0

    if discount > subtotal:
        discount = 0.0

    tax = (subtotal - discount) * TAX_RATE
    total = subtotal - discount + tax
    payment_method = request.form.get('payment_method', 'cash') or 'cash'

    db.execute(
        "INSERT INTO bills (order_id, subtotal, tax_amount, discount, total_amount, payment_method, paid) "
        "VALUES (?,?,?,?,?,?,1)",
        (order_id, round(subtotal, 2), round(tax, 2), round(discount, 2), round(total, 2), payment_method)
    )
    db.execute("UPDATE orders SET status='completed', updated_at=CURRENT_TIMESTAMP WHERE id=?", (order_id,))
    db.commit()
    flash(f'Bill generated successfully! Total: ₹{total:.2f}', 'success')
    return redirect(url_for('billing.receipt', order_id=order_id))

@billing_bp.route('/receipt/<int:order_id>')
def receipt(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('billing.index'))
    items = db.execute(
        "SELECT oi.*, mi.name FROM order_items oi JOIN menu_items mi ON oi.menu_item_id=mi.id "
        "WHERE oi.order_id=?", (order_id,)
    ).fetchall()
    bill = db.execute("SELECT * FROM bills WHERE order_id=?", (order_id,)).fetchone()
    return render_template('receipt.html', order=order, items=items, bill=bill, user=session['user'])
