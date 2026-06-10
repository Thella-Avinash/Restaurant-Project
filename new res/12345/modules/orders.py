from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from modules.database import get_db

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    orders = db.execute(
        "SELECT o.*, COUNT(oi.id) as item_count, COALESCE(SUM(oi.quantity*oi.unit_price),0) as subtotal "
        "FROM orders o LEFT JOIN order_items oi ON o.id=oi.order_id "
        "GROUP BY o.id ORDER BY o.created_at DESC"
    ).fetchall()
    menu_items = db.execute("SELECT * FROM menu_items WHERE available=1 ORDER BY category,name").fetchall()
    return render_template('orders.html', orders=orders, menu_items=menu_items, user=session['user'])

@orders_bp.route('/create', methods=['POST'])

def create():

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

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS customers(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        phone TEXT UNIQUE,

        email TEXT

        )
        """
    )


    cur = db.execute(
        """
        INSERT INTO orders(

        table_number,

        customer_name,

        customer_phone,

        customer_email,

        status,

        created_by

        )

        VALUES(
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
        )
        """,

        (
            request.form['table_number'],

            request.form.get(
                'customer_name',
                ''
            ),

            request.form.get(
                'customer_phone',
                ''
            ),

            request.form.get(
                'customer_email',
                ''
            ),

            'pending',

            session['user']['id']
        )
    )


    customer_phone = request.form.get(
        'customer_phone',
        ''
    )

    if customer_phone:

        exists = db.execute(

            """
            SELECT id
            FROM customers
            WHERE phone=?
            """,

            (
                customer_phone,
            )

        ).fetchone()


        if exists is None:

            db.execute(

                """
                INSERT INTO customers(

                name,

                phone,

                email

                )

                VALUES(
                ?,
                ?,
                ?
                )
                """,

           (
    request.form.get(
        'customer_name',
        ''
    ),

    customer_phone,

    request.form.get(
        'customer_email',
        ''
    )
)

            )


    db.commit()

    order_id = cur.lastrowid

    item_ids = request.form.getlist(
        'item_id[]'
    )

    quantities = request.form.getlist(
        'quantity[]'
    )

    notes_list = request.form.getlist(
        'notes[]'
    )


    for item_id, qty, note in zip(
        item_ids,
        quantities,
        notes_list
    ):

        if int(qty) > 0:

            price = db.execute(
                """
                SELECT price
                FROM menu_items
                WHERE id=?
                """,
                (
                    item_id,
                )
            ).fetchone()['price']


            db.execute(
                """
                INSERT INTO order_items(

                order_id,

                menu_item_id,

                quantity,

                unit_price,

                notes

                )

                VALUES(
                ?,
                ?,
                ?,
                ?,
                ?
                )
                """,

                (
                    order_id,
                    item_id,
                    int(qty),
                    price,
                    note
                )
            )


    db.commit()
    flash(
        f'Order #{order_id} created successfully!',
        'success'
    )
    return redirect(
        url_for(
            'orders.index'
        )
    )


@orders_bp.route('/update-status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    status = request.form.get('status')
    db.execute("UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, order_id))
    db.commit()
    return jsonify({'success': True})

@orders_bp.route('/view/<int:order_id>')
def view(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    items = db.execute(
        "SELECT oi.*, mi.name, mi.category FROM order_items oi "
        "JOIN menu_items mi ON oi.menu_item_id=mi.id WHERE oi.order_id=?", (order_id,)
    ).fetchall()
    bill = db.execute("SELECT * FROM bills WHERE order_id=?", (order_id,)).fetchone()
    return jsonify({
        'order': dict(order),
        'items': [dict(i) for i in items],
        'bill': dict(bill) if bill else None
    })

@orders_bp.route('/delete/<int:order_id>')
def delete(order_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    db.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    db.execute("DELETE FROM bills WHERE order_id=?", (order_id,))
    db.execute("DELETE FROM orders WHERE id=?", (order_id,))
    db.commit()
    flash('Order deleted!', 'success')
    return redirect(url_for('orders.index'))
