# CONZURA — Restaurant Management System
### Internship Project | Python Flask + SQLite

---

## 📋 Project Overview
A complete web-based Restaurant Management System built with Python (Flask) and SQLite, featuring:
- Admin & Staff Authentication
- Menu Management (Add/Edit/Delete)
- Order Management (Create, Update Status, View)
- Billing & Receipt Generation (with GST)
- Inventory Tracking with Low-Stock Alerts
- Sales Reports & Analytics (Charts)
- User Management (Admin only)

---

## 🚀 Quick Setup (VS Code)

### Step 1 — Open Project
Open the `restaurant_ms` folder in VS Code.

### Step 2 — Install Python Dependencies
Open the VS Code Terminal (`Ctrl + `` ` ``) and run:
```bash
pip install flask
```

### Step 3 — Run the App
```bash
python app.py
```

### Step 4 — Open in Browser
Visit: **http://localhost:5000**

---

## 🔑 Login Credentials
| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| Staff | staff    | staff123  |

---

## 📁 Project Structure
```
restaurant_ms/
├── app.py                  ← Main Flask application
├── requirements.txt        ← Python dependencies
├── restaurant.db           ← SQLite database (auto-created)
├── modules/
│   ├── database.py         ← DB init & connection
│   ├── auth.py             ← Login/Logout/Users
│   ├── menu.py             ← Menu CRUD
│   ├── orders.py           ← Order management
│   ├── billing.py          ← Bill generation
│   ├── inventory.py        ← Inventory tracking
│   └── reports.py          ← Reports & analytics
└── templates/
    ├── base.html           ← Shared layout
    ├── login.html          ← Login page
    ├── dashboard.html      ← Main dashboard
    ├── menu.html           ← Menu management
    ├── orders.html         ← Orders list & creation
    ├── billing.html        ← All bills
    ├── receipt.html        ← Bill receipt / print
    ├── inventory.html      ← Inventory management
    ├── reports.html        ← Charts & analytics
    └── users.html          ← User management
```

---

## 🛠️ Technologies Used
| Component   | Technology          |
|-------------|---------------------|
| Language    | Python 3.x          |
| Framework   | Flask               |
| Database    | SQLite (built-in)   |
| Frontend    | HTML5, CSS3, JS     |
| Charts      | Chart.js            |
| Icons       | Font Awesome 6      |
| Fonts       | Google Fonts        |

---

## 🌟 Features
- **Dark, luxury UI** with gold accent theme
- **Real-time clock** on dashboard
- **Live revenue charts** (7/14/30-day view)
- **Category filter** on menu page
- **Order status** updated live (no page reload)
- **Print receipt** button for billing
- **Low stock alerts** banner in inventory
- **Tax calculation** auto (5% GST)
- **Demo data** pre-loaded (10 menu items, 10 inventory items)

---

## 📌 Notes
- The database (`restaurant.db`) is created automatically on first run.
- Default admin cannot be deleted.
- Tax rate is set to 5% GST (editable in `modules/billing.py`).

---

*Developed as an internship project — CONZURA Restaurant Management System*
