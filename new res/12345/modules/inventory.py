from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.database import get_db

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    items = db.execute("SELECT * FROM inventory ORDER BY category, item_name").fetchall()
    low_stock = [i for i in items if i['quantity'] <= i['min_quantity']]
    return render_template('inventory.html', items=items, low_stock=low_stock, user=session['user'])

@inventory_bp.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    db.execute(
        "INSERT INTO inventory (item_name, category, quantity, unit, min_quantity, cost_per_unit, supplier) "
        "VALUES (?,?,?,?,?,?,?)",
        (request.form['item_name'], request.form['category'], float(request.form['quantity']),
         request.form['unit'], float(request.form['min_quantity']),
         float(request.form.get('cost_per_unit', 0)), request.form.get('supplier', ''))
    )
    db.commit()
    flash('Inventory item added!', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/update/<int:item_id>', methods=['POST'])
def update(item_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    db.execute(
        "UPDATE inventory SET item_name=?, category=?, quantity=?, unit=?, "
        "min_quantity=?, cost_per_unit=?, supplier=?, last_updated=CURRENT_TIMESTAMP WHERE id=?",
        (request.form['item_name'], request.form['category'], float(request.form['quantity']),
         request.form['unit'], float(request.form['min_quantity']),
         float(request.form.get('cost_per_unit', 0)), request.form.get('supplier', ''), item_id)
    )
    db.commit()
    flash('Inventory updated!', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/delete/<int:item_id>')
def delete(item_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    db.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    db.commit()
    flash('Item removed from inventory!', 'success')
    return redirect(url_for('inventory.index'))
