import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

# ============================================================================
# 📋 COMPLETE TEMPLATE LIST (ALL 108 TEMPLATES)
# ============================================================================
# This documents ALL templates used in routes.py for reference
# ============================================================================
TEMPLATES = {
    # Root Templates (3)
    'root': [
        'customer-site.html',
        'dashboard.html',
        'base.html',
    ],
    
    # Authentication (1)
    'auth': [
        'auth/login.html',
    ],
    
    # Products (4)
    'products': [
        'products/index.html',
        'products/form.html',
        'products/bom.html',
        'products/labels.html',
    ],
    
    # Inquiries (4)
    'inquiries': [
        'inquiries/index.html',
        'inquiries/form.html',
        'inquiries/edit.html',
        'inquiries/invoice.html',
    ],
    
    # Orders (5)
    'orders': [
        'orders/index.html',
        'orders/form.html',
        'orders/view.html',
        'orders/edit.html',
        'orders/invoice.html',
    ],
    
    # Customers (4)
    'customers': [
        'customers/index.html',
        'customers/form.html',
        'customers/painting_pricing.html',
        'customers/merge.html',
    ],
    
    # Suppliers (3)
    'suppliers': [
        'suppliers/index.html',
        'suppliers/form.html',
        'suppliers/history.html',
    ],
    
    # Purchase Orders (4)
    'purchase_orders': [
        'purchase_orders/index.html',
        'purchase_orders/form.html',
        'purchase_orders/view.html',
        'purchase_orders/receive.html',
    ],
    
    # Goods Receipts (2)
    'goods_receipts': [
        'goods_receipts/index.html',
        'goods_receipts/view.html',
    ],
    
    # Warehouses (3)
    'warehouses': [
        'warehouses/index.html',
        'warehouses/form.html',
        'warehouses/stock.html',
    ],
    
    # Stock Transfers (3)
    'stock_transfers': [
        'stock_transfers/index.html',
        'stock_transfers/form.html',
        'stock_transfers/view.html',
    ],
    
    # Material Batches (1)
    'material_batches': [
        'material_batches/index.html',
    ],
    
    # Supplier Invoices (2)
    'supplier_invoices': [
        'supplier_invoices/index.html',
        'supplier_invoices/form.html',
    ],
    
    # Production (6)
    'production': [
        'production/dashboard.html',
        'production/batches.html',
        'production/batch_form.html',
        'production/batch_view.html',
        'production/batch_complete.html',
        'production/reports.html',
    ],
    
    # Materials (2)
    'materials': [
        'materials/index.html',
        'materials/form.html',
    ],
    
    # Quality Control (8)
    'qc': [
        'qc/parameters.html',
        'qc/parameter_form.html',
        'qc/results_form.html',
        'qc/complaints.html',
        'qc/complaint_form.html',
        'qc/capa.html',
        'qc/calibration.html',
        'qc/coa.html',
    ],
    
    # Reports (6)
    'reports': [
        'reports/dashboard.html',
        'reports/sales_analysis.html',
        'reports/inventory_valuation.html',
        'reports/customer_purchase_history.html',
        'reports/production_efficiency.html',
        'reports/material_consumption.html',
    ],
    
    # Analytics (1)
    'analytics': [
        'analytics/dashboard.html',
    ],
    
    # Settings (1)
    'settings': [
        'settings/index.html',
    ],
    
    # Payroll/Employees (10)
    'payroll': [
        'payroll/index.html',
        'payroll/form.html',
        'payroll/attendance.html',
        'payroll/attendance_history.html',
        'payroll/timesheets.html',
        'payroll/timesheet_form.html',
        'payroll/leave_requests.html',
        'payroll/leave_form.html',
        'payroll/payments.html',
        'payroll/payment_form.html',
    ],
    
    # Expenses (2)
    'expenses': [
        'expenses/index.html',
        'expenses/form.html',
    ],
    
    # Accounting (17)
    'accounting': [
        'accounting/index.html',
        'accounting/dashboard.html',
        'accounting/chart_of_accounts.html',
        'accounting/account_form.html',
        'accounting/journal_entries.html',
        'accounting/journal_entry_form.html',
        'accounting/journal_entry_view.html',
        'accounting/general_ledger.html',
        'accounting/trial_balance.html',
        'accounting/payment_vouchers.html',
        'accounting/payment_voucher_form.html',
        'accounting/payment_voucher_view.html',
        'accounting/receipt_vouchers.html',
        'accounting/receipt_voucher_form.html',
        'accounting/receipt_voucher_view.html',
        'accounting/bank_accounts.html',
        'accounting/bank_reconciliation.html',
        'accounting/audit_log.html',
        'accounting/periods.html',
        'accounting/period_form.html',
    ],
    
    # Financials (3)
    'financials': [
        'financials/profit_loss.html',
        'financials/balance_sheet.html',
        'financials/cash_flow.html',
    ],
    
    # Painting Service (7)
    'painting': [
        'painting/dashboard.html',
        'painting/prices.html',
        'painting/price_form.html',
        'painting/orders.html',
        'painting/order_form.html',
        'painting/order_view.html',
        'painting/invoice.html',
    ],
    
    # Tax/FBR (4)
    'tax': [
        'tax/fbr_invoices.html',
        'tax/returns.html',
        'tax/return_form.html',
        'tax/reports/sales_tax.html',
    ],
}

# Total: 108 templates
TOTAL_TEMPLATES = sum(len(templates) for templates in TEMPLATES.values())

def create_app():
    PROJECT_ROOT = Path(__file__).parent.parent
    TEMPLATES_FOLDER = PROJECT_ROOT / 'templates'
    STATIC_DIR = PROJECT_ROOT / 'static'
    
    app = Flask(__name__, 
                template_folder=str(TEMPLATES_FOLDER),
                static_folder=str(STATIC_DIR))
    
    # Apply ProxyFix for Cloud Run / reverse proxy (trusts X-Forwarded-For headers)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 5,
        'max_overflow': 10,
    }
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    # SameSite=None + Secure=True allows cookies in all contexts including iframes
    # (Replit preview and Cloud Run both serve over HTTPS, so Secure is always safe)
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Validate DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    if db_url and isinstance(db_url, str) and 'postgres' in db_url and 'connect_timeout' not in db_url:
        sep = '&' if '?' in db_url else '?'
        db_url += f"{sep}connect_timeout=10"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    
    # Ensure sslmode=require for Neon
    if db_url and isinstance(db_url, str) and 'postgres' in db_url and 'sslmode' not in db_url:
        sep = '&' if '?' in db_url else '?'
        db_url += f"{sep}sslmode=require"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    
    # Make datetime and current_year available in all templates
    @app.context_processor
    def inject_globals():
        return dict(datetime=datetime, timedelta=timedelta, current_year=datetime.utcnow().year)
    
    # Dev proxy: forward /__mockup/* to Vite dev server on port 3001
    @app.route('/__mockup/', defaults={'path': ''})
    @app.route('/__mockup/<path:path>')
    def mockup_proxy(path):
        target = f"http://127.0.0.1:3001/__mockup/{path}"
        if request.query_string:
            target += '?' + request.query_string.decode()
        try:
            req = urllib.request.Request(target, headers={
                k: v for k, v in request.headers if k.lower() not in ('host', 'content-length')
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read()
                excluded = {'transfer-encoding', 'connection', 'keep-alive'}
                headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
                return Response(content, status=resp.status, headers=headers)
        except urllib.error.URLError:
            return Response("Mockup sandbox not running", status=503)

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Create tables and admin user
    with app.app_context():
        try:
            app.logger.info("🏗️ Creating/Verifying tables...")
            db.create_all()
            app.logger.info("✅ Tables verified/created.")
            
            # Create admin user if not exists
            from app.models import User
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@ampoulex.com',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                app.logger.info("✅ Admin user created (admin/admin123).")
            else:
                app.logger.info("✅ Admin user already exists.")
                
        except Exception as e:
            app.logger.error(f"❌ Database setup error: {e}")
            raise
    
    app.logger.info("🗺️ Registering routes...")
    app.logger.info(f"📋 Total templates documented: {TOTAL_TEMPLATES}")
    app.logger.info("✅ Routes registered successfully.")
    
    return app