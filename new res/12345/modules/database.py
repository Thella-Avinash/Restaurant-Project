# database.py — get_db is injected by app.py at startup
# This stub exists so modules can import get_db
# The real get_db is patched in by app.py before blueprints are registered

import sqlite3, os
from flask import g

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'restaurant.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db
