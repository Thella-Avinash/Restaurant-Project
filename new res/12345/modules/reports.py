from flask import Blueprint, render_template, request, redirect, url_for, session, flash, flash, jsonify
from modules.database import get_db

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if session['user']['role'] == 'admin':
        flash('Access denied. Admin can only manage the Menu.', 'error')
        return redirect(url_for('menu.index'))
    db = get_db()
    # Daily report
    daily = db.execute(
        "SELECT DATE(created_at) as date, COUNT(*) as orders, SUM(total_amount) as revenue "
        "FROM bills WHERE created_at >= DATE('now','-30 days') "
        "GROUP BY DATE(created_at) ORDER BY date DESC"
    ).fetchall()
    # Top items
    top_items = db.execute(
        "SELECT mi.name, SUM(oi.quantity) as total_qty, SUM(oi.quantity*oi.unit_price) as revenue "
        "FROM order_items oi JOIN menu_items mi ON oi.menu_item_id=mi.id "
        "GROUP BY mi.id ORDER BY total_qty DESC LIMIT 10"
    ).fetchall()
    # Category revenue
    category_rev = db.execute(
        "SELECT mi.category, SUM(oi.quantity*oi.unit_price) as revenue "
        "FROM order_items oi JOIN menu_items mi ON oi.menu_item_id=mi.id "
        "GROUP BY mi.category ORDER BY revenue DESC"
    ).fetchall()
    summary = db.execute(
        "SELECT COALESCE(SUM(total_amount),0) as total_revenue, COUNT(*) as total_bills "
        "FROM bills WHERE paid=1"
    ).fetchone()
    return render_template('reports.html', daily=daily, top_items=top_items,
                           category_rev=category_rev, summary=summary, user=session['user'])

@reports_bp.route('/api/chart-data')
def chart_data():
    db = get_db()
    days = request.args.get('days', 7, type=int)
    daily = db.execute(
        f"SELECT DATE(created_at) as date, SUM(total_amount) as revenue "
        f"FROM bills WHERE created_at >= DATE('now','-{days} days') "
        f"GROUP BY DATE(created_at) ORDER BY date"
    ).fetchall()
    categories = db.execute(
        "SELECT mi.category, SUM(oi.quantity*oi.unit_price) as revenue "
        "FROM order_items oi JOIN menu_items mi ON oi.menu_item_id=mi.id "
        "GROUP BY mi.category"
    ).fetchall()
    return jsonify({
        'daily': {'labels': [r['date'] for r in daily], 'values': [float(r['revenue'] or 0) for r in daily]},
        'categories': {'labels': [r['category'] for r in categories], 'values': [float(r['revenue'] or 0) for r in categories]}
    })
