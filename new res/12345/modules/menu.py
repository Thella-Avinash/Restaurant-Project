from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from modules.database import get_db
import os
from modules.database import get_db
from werkzeug.utils import secure_filename
from flask import current_app
menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    db = get_db()
    items = db.execute("SELECT * FROM menu_items ORDER BY category, name").fetchall()
    categories = db.execute("SELECT DISTINCT category FROM menu_items").fetchall()
    return render_template('menu.html', items=items, categories=categories, user=session['user'])




@menu_bp.route('/add', methods=['POST'])
def add():

    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if session['user']['role'] != 'admin':
        flash('Only Admin can add menu items.', 'error')
        return redirect(url_for('menu.index'))

    db = get_db()

    image = request.files.get("image")

    filename = None

    db.execute(

        """

        INSERT INTO menu_items(

        name,

        category,

        price,

        description,

        image

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

            request.form["name"],

            request.form["category"],

            float(request.form["price"]),

            request.form.get(
                "description",
                ""
            ),

            filename

        )

    )

    db.commit()

    flash(
        'Menu item added successfully!',
        'success'
    )

    return redirect(
        url_for(
            'menu.index'
        )
    )




@menu_bp.route('/edit/<int:item_id>', methods=['POST'])
def edit(item_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] != 'admin':
        flash('Only Admin can edit menu items.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    db.execute("UPDATE menu_items SET name=?, category=?, price=?, description=?, available=? WHERE id=?",
               (request.form['name'], request.form['category'], float(request.form['price']),
                request.form.get('description', ''), int(request.form.get('available', 1)), item_id))
    db.commit()
    flash('Menu item updated!', 'success')
    return redirect(url_for('menu.index'))

@menu_bp.route('/delete/<int:item_id>')
def delete(item_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] != 'admin':
        flash('Only Admin can delete menu items.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    db.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
    db.commit()
    flash('Menu item deleted!', 'success')
    return redirect(url_for('menu.index'))

@menu_bp.route('/api/items')
def api_items():
    db = get_db()
    items = db.execute("SELECT * FROM menu_items WHERE available=1 ORDER BY category, name").fetchall()
    return jsonify([dict(i) for i in items])
@menu_bp.route('/public')
def public_menu():

    db = get_db()

    items = db.execute(
        """
        SELECT *
        FROM menu_items
        WHERE available = 1
        ORDER BY category,name
        """
    ).fetchall()

    categories = db.execute(
        """
        SELECT DISTINCT category
        FROM menu_items
        """
    ).fetchall()

    return render_template(
        'public_menu.html',
        items=items,
        categories=categories
    )