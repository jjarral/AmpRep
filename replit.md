# Ampoulex ERP System

## Overview
Ampoulex is a comprehensive Enterprise Resource Planning (ERP) / Business Management System built with Flask. It handles accounting, inventory, production, quality control, payroll, and sales operations, configured for a company operating in Pakistan (PKR currency, FBR tax compliance).

## Architecture
- **Backend:** Python Flask 3.0 with SQLAlchemy ORM
- **Database:** PostgreSQL (Replit built-in, or Cloud SQL on GCP)
- **Real-time:** Flask-SocketIO with eventlet worker
- **Frontend:** AdminLTE 3.2, Bootstrap 4.6, jQuery, Chart.js, DataTables, SweetAlert2 (CDN)
- **Theme:** Navy (#0c2340) + Gold (#c8a84b) design system — Inter font, applied system-wide via CSS variables in base.html
- **Reporting:** ReportLab (PDF), Openpyxl (Excel), pandas

## Project Structure
```
app/
  __init__.py     - App factory, extensions, context processor
  routes.py       - All route handlers (~5400 lines)
  models.py       - SQLAlchemy models
  forms.py        - Flask-WTF forms
  utils/          - Tax calculator and helpers
  email_helper.py - Email utilities
templates/        - 108 Jinja2 templates organized by module
static/           - CSS, JS, images, Excel templates
run.py            - Dev entry point (python run.py → port 5000)
wsgi.py           - Production WSGI entry (wsgi:application)
Dockerfile        - Cloud Run deployment config
requirements.txt  - Python dependencies
```

## Running the App
- **Dev:** `python run.py` → http://localhost:5000
- **Default Login:** admin / admin123 (auto-created on first run)
- **Production (Cloud Run):** `gunicorn --bind :$PORT --worker-class eventlet -w 1 wsgi:application`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-set by Replit)
- `SECRET_KEY` - Flask session secret key
- `FLASK_ENV` - Set to `production` in Cloud Run to enable secure cookies
- `PORT` - Server port (Cloud Run sets this; default 8080)

## Key Modules
- **Sales:** Inquiries, Orders, Customers, Products
- **Accounting:** Chart of accounts, journal entries, bank reconciliation, audit log
- **Inventory:** Warehouses, stock transfers, purchase orders, GRNs
- **Production:** Batch management, BOM, production reports
- **Quality Control:** Parameters, CAPA, calibration, COA
- **Payroll:** Employees, attendance, timesheets, leave, salary slips
- **Financials:** Profit & Loss, Balance Sheet, Cash Flow
- **Analytics:** Advanced analytics dashboard
- **Reporting:** Excel and PDF report generation
- **Tax/FBR:** FBR invoice compliance, sales tax reports
- **Painting:** Painting service orders and pricing

## Bugs Fixed (Setup Stabilization)
1. **Blueprint route conflict** — `favicon.ico` moved from app-level to Blueprint
2. **Missing CDN assets** — SweetAlert2 loaded from CDN in both base templates
3. **`integer()` undefined** — replaced with `int(... or 0)` in product routes
4. **`current_year` missing** — added to context processor in `app/__init__.py`
5. **SocketIO wrong path** — removed incorrect `path: '/socket.io/admin'` option
6. **Dockerfile CMD** — fixed to use `wsgi:application` with eventlet worker
7. **`eventlet` in requirements** — added `eventlet>=0.33.3`
8. **ProxyFix** — added `werkzeug.middleware.proxy_fix.ProxyFix` for Cloud Run HTTPS
9. **Session cookies** — added `SESSION_COOKIE_SAMESITE=Lax` for iframe proxy support
10. **AuditLog model** — kept `timestamp` column; added `created_at` property alias
11. **SQLAlchemy overlaps** — fixed `InquiryItem.inquiry` and `OrderItem.order` relationships
12. **Analytics 500** — added all missing variables to `analytics_dashboard` route
13. **`strftime` on PostgreSQL** — replaced `db.func.strftime` with `db.func.to_char`
14. **Balance sheet variable order** — `accounts_payable` now computed before use
15. **Balance sheet missing var** — added `long_term_liabilities` to template context
16. **SQLAlchemy 2.0 `case()` syntax** — fixed list-of-tuples to positional tuple
17. **Cash flow variable names** — aligned route variable names with template expectations
18. **Login active check** — added `user.is_active` check; added `remember_me` support
19. **Painting dashboard** — replaced `db.func.strftime` with Python date range filter
