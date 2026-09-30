import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta

try:
    from flask import Flask, jsonify, request, Response
except ModuleNotFoundError as e:
    raise RuntimeError(
        "Missing required dependency: Flask. Install dependencies with `python -m pip install -r requirements.txt`."
    ) from e

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions at module level (required for Flask app factory)
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

# ============================================================================
# 📋 COMPLETE TEMPLATE LIST (ALL 108 TEMPLATES)
# ============================================================================
TEMPLATES = {
    'root': ['customer-site.html', 'dashboard.html', 'base.html'],
    'auth': ['auth/login.html'],
    'products': ['products/index.html', 'products/form.html', 'products/bom.html', 'products/labels.html'],
    'inquiries': ['inquiries/index.html', 'inquiries/form.html', 'inquiries/edit.html', 'inquiries/invoice.html'],
    'orders': ['orders/index.html', 'orders/form.html', 'orders/view.html', 'orders/edit.html', 'orders/invoice.html'],
    'customers': ['customers/index.html', 'customers/form.html', 'customers/painting_pricing.html', 'customers/merge.html', 'customers/catalogue.html', 'customers/inquiry.html'],
    'suppliers': ['suppliers/index.html', 'suppliers/form.html', 'suppliers/history.html'],
    'purchase_orders': ['purchase_orders/index.html', 'purchase_orders/form.html', 'purchase_orders/view.html', 'purchase_orders/receive.html'],
    'goods_receipts': ['goods_receipts/index.html', 'goods_receipts/view.html'],
    'warehouses': ['warehouses/index.html', 'warehouses/form.html', 'warehouses/stock.html'],
    'stock_transfers': ['stock_transfers/index.html', 'stock_transfers/form.html', 'stock_transfers/view.html'],
    'material_batches': ['material_batches/index.html'],
    'supplier_invoices': ['supplier_invoices/index.html', 'supplier_invoices/form.html'],
    'production': ['production/dashboard.html', 'production/batches.html', 'production/batch_form.html', 'production/batch_view.html', 'production/batch_complete.html', 'production/reports.html'],
    'materials': ['materials/index.html', 'materials/form.html'],
    'qc': ['qc/parameters.html', 'qc/parameter_form.html', 'qc/results_form.html', 'qc/complaints.html', 'qc/complaint_form.html', 'qc/capa.html', 'qc/calibration.html', 'qc/coa.html'],
    'reports': ['reports/dashboard.html', 'reports/sales_analysis.html', 'reports/inventory_valuation.html', 'reports/customer_purchase_history.html', 'reports/production_efficiency.html', 'reports/material_consumption.html'],
    'analytics': ['analytics/dashboard.html'],
    'settings': ['settings/index.html'],
    'payroll': ['payroll/index.html', 'payroll/form.html', 'payroll/attendance.html', 'payroll/attendance_history.html', 'payroll/timesheets.html', 'payroll/timesheet_form.html', 'payroll/leave_requests.html', 'payroll/leave_form.html', 'payroll/payments.html', 'payroll/payment_form.html'],
    'expenses': ['expenses/index.html', 'expenses/form.html'],
    'accounting': ['accounting/index.html', 'accounting/dashboard.html', 'accounting/chart_of_accounts.html', 'accounting/account_form.html', 'accounting/journal_entries.html', 'accounting/journal_entry_form.html', 'accounting/journal_entry_view.html', 'accounting/general_ledger.html', 'accounting/trial_balance.html', 'accounting/payment_vouchers.html', 'accounting/payment_voucher_form.html', 'accounting/payment_voucher_view.html', 'accounting/receipt_vouchers.html', 'accounting/receipt_voucher_form.html', 'accounting/receipt_voucher_view.html', 'accounting/bank_accounts.html', 'accounting/bank_reconciliation.html', 'accounting/audit_log.html', 'accounting/periods.html', 'accounting/period_form.html'],
    'financials': ['financials/profit_loss.html', 'financials/balance_sheet.html', 'financials/cash_flow.html'],
    'painting': ['painting/dashboard.html', 'painting/prices.html', 'painting/price_form.html', 'painting/orders.html', 'painting/order_form.html', 'painting/order_view.html', 'painting/invoice.html'],
    'tax': ['tax/fbr_invoices.html', 'tax/returns.html', 'tax/return_form.html', 'tax/reports/sales_tax.html'],
}

TOTAL_TEMPLATES = sum(len(templates) for templates in TEMPLATES.values())


def _is_local_environment() -> bool:
    """Detect if running on localhost/local development."""
    if os.environ.get('FLASK_ENV') == 'development':
        return True
    if os.environ.get('DEBUG') in ('1', 'true', 'True', True):
        return True
    cloud_indicators = [
        'VERCEL', 'VERCEL_REGION', 'GAE_ENV', 'GOOGLE_CLOUD_PROJECT',
        'AWS_LAMBDA_FUNCTION_NAME', 'DYNO', 'KUBERNETES_SERVICE_HOST', 'RENDER',
    ]
    if any(os.environ.get(ind) for ind in cloud_indicators):
        return False
    return True


def create_app():
    PROJECT_ROOT = Path(__file__).parent.parent
    TEMPLATES_FOLDER = PROJECT_ROOT / 'templates'
    STATIC_DIR = PROJECT_ROOT / 'static'
    
    app = Flask(__name__, 
                template_folder=str(TEMPLATES_FOLDER),
                static_folder=str(STATIC_DIR))
    
    # Apply ProxyFix for reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Configuration
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key and not _is_local_environment():
        raise RuntimeError('SECRET_KEY must be set for production deployment.')
    app.config['SECRET_KEY'] = secret_key or 'dev-only-key-change-before-deployment'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 5,
        'max_overflow': 10,
    }
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

    # ────────────────────────────────────────────────────────────────
    # 🗄️ Database Configuration
    # ────────────────────────────────────────────────────────────────
    db_url = (
        os.environ.get('DATABASE_URL') 
        or os.environ.get('NEON_DATABASE_URL')
        or os.environ.get('POSTGRES_URL')
        or os.environ.get('POSTGRES_PRISMA_URL')
        or os.environ.get('DATABASE_PRIVATE_URL')
    )

    app.logger.info(f"🔍 Env check: DATABASE_URL={bool(os.environ.get('DATABASE_URL'))}, "
                    f"POSTGRES_URL={bool(os.environ.get('POSTGRES_URL'))}, "
                    f"VERCEL={bool(os.environ.get('VERCEL'))}")

    if db_url and isinstance(db_url, str) and 'postgres' in db_url:
        if 'connect_timeout' not in db_url:
            sep = '&' if '?' in db_url else '?'
            db_url += f"{sep}connect_timeout=10"
        if 'sslmode' not in db_url:
            sep = '&' if '?' in db_url else '?'
            db_url += f"{sep}sslmode=require"
        
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SESSION_COOKIE_SECURE'] = True
        app.logger.info(f"🔗 Connected to Postgres: {db_url.split('@')[-1].split('?')[0]}")
        
    elif _is_local_environment():
        sqlite_path = PROJECT_ROOT / 'ampoulex.db'
        db_url = f"sqlite:///{sqlite_path}"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SESSION_COOKIE_SECURE'] = False
        app.logger.info(f"🗄️ Using local SQLite: {sqlite_path}")
        
    else:
        available_vars = [k for k in os.environ.keys() if 'POSTGRES' in k or 'DATABASE' in k or 'NEON' in k]
        raise RuntimeError(
            f'DATABASE_URL or another supported PostgreSQL URL must be set for production deployment.\n'
            f'Found these related env vars: {available_vars if available_vars else "NONE"}'
        )

    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # ────────────────────────────────────────────────────────────────
    # 🔐 Flask-Login: User loader (MUST be inside create_app)
    # ────────────────────────────────────────────────────────────────
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Lazy import to avoid circular dependency
        return User.query.get(int(user_id))

    # ────────────────────────────────────────────────────────────────
    # 🌐 Context Processors (MUST be inside create_app)
    # ────────────────────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        return dict(datetime=datetime, timedelta=timedelta, current_year=datetime.utcnow().year)

    @app.context_processor
    def inject_business_settings():
        try:
            from .models import BusinessSettings  # Lazy import
            settings = BusinessSettings.query.first()
            if not settings:
                settings = BusinessSettings()
                db.session.add(settings)
                db.session.commit()
            return dict(business=settings)
        except Exception as e:
            app.logger.warning(f"⚠️ Business settings fallback: {e}")
            class DefaultSettings:
                company_name = 'AMPOULEX'
                phone_1 = '0340-5336238'
                phone_2 = '0331-9980906'
                email = 'info@ampoulex.com'
                website = 'www.ampoulex.com'
                address = 'Malik Arshad Farm House (Malik Akram Street), Darbar-e-Kareemi Stop, G.T Road Wah Cantt, Rawalpindi, Punjab, 47000'
                ntn = '2812596-7'
                strn = '37406-5984131-3'
            return dict(business=DefaultSettings())

    # ────────────────────────────────────────────────────────────────
    # 🔧 Dev Proxy Route
    # ────────────────────────────────────────────────────────────────
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

    # ────────────────────────────────────────────────────────────────
    # 🗺️ Register Blueprints
    # ────────────────────────────────────────────────────────────────
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # ────────────────────────────────────────────────────────────────
    # 🏗️ Database Setup (tables + admin user)
    # ────────────────────────────────────────────────────────────────
    with app.app_context():
        try:
            app.logger.info("🏗️ Creating/Verifying tables...")
            db.create_all()
            app.logger.info("✅ Tables verified/created.")
            
            from .models import User  # Lazy import
            if not User.query.filter_by(role='admin').first():
                admin_username = os.environ.get('INITIAL_ADMIN_USERNAME')
                admin_email = os.environ.get('INITIAL_ADMIN_EMAIL')
                admin_password = os.environ.get('INITIAL_ADMIN_PASSWORD')
                admin_bootstrap = (admin_username, admin_email, admin_password)
                if any(admin_bootstrap) and not all(admin_bootstrap):
                    raise RuntimeError(
                        'Set all of INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_EMAIL, '
                        'and INITIAL_ADMIN_PASSWORD to bootstrap an admin account.'
                    )
                if not all(admin_bootstrap):
                    if not _is_local_environment():
                        raise RuntimeError(
                            'No admin account exists. Set INITIAL_ADMIN_USERNAME, '
                            'INITIAL_ADMIN_EMAIL, and INITIAL_ADMIN_PASSWORD to bootstrap one.'
                        )
                    app.logger.warning('No local admin account exists; skipping admin bootstrap.')
                else:
                    admin = User(
                        username=admin_username,
                        email=admin_email,
                        role='admin',
                        is_active=True
                    )
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
                    app.logger.info("✅ Initial admin user created.")
            else:
                app.logger.info("✅ Admin user already exists.")
                
        except Exception as e:
            app.logger.error(f"❌ Database setup error: {e}")
            raise
    
    app.logger.info("🗺️ Registering routes...")
    app.logger.info(f"📋 Total templates documented: {TOTAL_TEMPLATES}")
    app.logger.info("✅ Routes registered successfully.")
    
    return app  # ✅ CORRECT PLACEMENT: End of create_app()
