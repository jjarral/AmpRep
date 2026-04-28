from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def record_failed_login(self):
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def record_successful_login(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    product_type = db.Column(db.String(50), nullable=True)
    specification = db.Column(db.String(255), nullable=True)
    base_name = db.Column(db.String(120), nullable=True)
    volume_cc = db.Column(db.Float)
    glass_type = db.Column(db.String(20))
    neck_finish = db.Column(db.String(20))
    sku = db.Column(db.String(50))
    color = db.Column(db.String(50), nullable=True)
    
    # ✅ ADD ALL THESE MISSING COLUMNS:
    stock = db.Column(db.Integer, default=0)
    base_price = db.Column(db.Integer, default=0)
    price_per_unit = db.Column(db.Numeric(10, 4))
    unit_price = db.Column(db.Numeric(10, 4))
    
    # ✅ DIMENSION FIELDS:
    body_diameter = db.Column(db.Float, default=0)
    overall_length = db.Column(db.Float, default=0)
    sealing_point = db.Column(db.Float, default=0)
    body_length = db.Column(db.Float, default=0)
    stem_diameter = db.Column(db.Float, default=0)
    wall_thickness = db.Column(db.Float, default=0)
    
    # ✅ ADDITIONAL FIELDS:
    material_type = db.Column(db.String(50), nullable=True)
    usp_type = db.Column(db.String(50), nullable=True)
    shape_type = db.Column(db.String(50), nullable=True)
    dimensions = db.Column(db.String(200), nullable=True)
    use_case = db.Column(db.Text, nullable=True)
    
    # ✅ PAINTING FIELDS:
    paint_color = db.Column(db.String(50), nullable=True)
    paint_type = db.Column(db.String(50), nullable=True)
    printing_method = db.Column(db.String(50), nullable=True)
    
    # ✅ STATUS:
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    payment_terms = db.Column(db.String(20), default='cash')
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    credit_limit = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    custom_prices = db.relationship('CustomerProductPrice', backref='customer', lazy=True)
    painting_prices = db.relationship('CustomerPaintingPrice', backref='customer', lazy=True) 
    orders = db.relationship('Order', backref='customer', lazy=True)

class CustomerProductPrice(db.Model):
    __tablename__ = 'customer_product_price'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    agreed_price = db.Column(db.Float, nullable=False)
    payment_terms = db.Column(db.String(50))
    
    # customer = db.relationship(...)  # Removed - created by Customer.custom_prices backref
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref

class Inquiry(db.Model):
    __tablename__ = 'inquiry'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_number = db.Column(db.String(20), unique=True)
    customer_name = db.Column(db.String(100), nullable=False)
    business_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), default='new')
    notes = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ✅ Fix this line (remove backref to avoid conflict):
    inquiry_items = db.relationship('InquiryItem', lazy=True)
class InquiryItem(db.Model):
    __tablename__ = 'inquiry_item'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiry.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inquiry = db.relationship('Inquiry', lazy=True, overlaps="inquiry_items")
    
    # ✅ Add product relationship (without backref to avoid conflicts):
    product = db.relationship('Product', lazy=True) 
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiry.id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='unpaid')
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.DateTime)
    paid_amount = db.Column(db.Float, default=0)
    customer_name_snapshot = db.Column(db.String(100))
    customer_business_snapshot = db.Column(db.String(100))
    customer_phone_snapshot = db.Column(db.String(20))
    customer_email_snapshot = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', lazy=True)  # backref removed

    # customer = db.relationship(...)  # Removed - created by Customer.custom_prices backref
    # inquiry = db.relationship(...)  # Removed - created by Inquiry.inquiry_items backref

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Relationship to Product (no backref to avoid conflict)
    product = db.relationship('Product', lazy=True)
    order = db.relationship('Order', lazy=True, overlaps="order_items")
    
class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    department = db.Column(db.String(50))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    cnic = db.Column(db.String(15), unique=True)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    base_salary = db.Column(db.Float, nullable=False)
    payment_frequency = db.Column(db.String(20), default='monthly')
    bank_account = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    outstanding_loan = db.Column(db.Float, default=0)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    paid_by = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    reference_number = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Accounting(db.Model):
    __tablename__ = 'accounting'
    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10))
    date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(100))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CompanySetting(db.Model):
    __tablename__ = 'company_setting'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaxSetting(db.Model):
    __tablename__ = 'tax_setting'
    id = db.Column(db.Integer, primary_key=True)
    tax_free_threshold = db.Column(db.Float, default=600000)
    top_bracket_threshold = db.Column(db.Float, default=4100000)
    high_earner_threshold = db.Column(db.Float, default=10000000)
    top_bracket_fixed_tax = db.Column(db.Float, default=616000)
    top_bracket_rate = db.Column(db.Float, default=35)
    high_earner_surcharge = db.Column(db.Float, default=9)
    tax_slabs = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StockAdjustment(db.Model):
    __tablename__ = 'stock_adjustment'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    adjusted_by = db.Column(db.String(100))
    adjustment_date = db.Column(db.DateTime, default=datetime.utcnow)
    # product = db.relationship('Product')  # Removed - created by Product.order_items backref

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50))
    generated_by = db.Column(db.String(100))
    parameters = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    hours_worked = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='present')
    notes = db.Column(db.Text)
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='attendance_records')

class Timesheet(db.Model):
    __tablename__ = 'timesheet'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), default='weekly')
    regular_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    total_hours = db.Column(db.Float, default=0)
    leave_days = db.Column(db.Float, default=0)
    sick_days = db.Column(db.Float, default=0)
    absent_days = db.Column(db.Float, default=0)
    hourly_rate = db.Column(db.Float, default=0)
    overtime_rate = db.Column(db.Float, default=0)
    regular_pay = db.Column(db.Float, default=0)
    overtime_pay = db.Column(db.Float, default=0)
    deductions = db.Column(db.Float, default=0)
    net_pay = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='draft')
    submitted_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='timesheets')

class LeaveRequest(db.Model):
    __tablename__ = 'leave_request'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    leave_type = db.Column(db.String(30), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='leave_requests')

class PayrollPayment(db.Model):
    __tablename__ = 'payroll_payment'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    timesheet_id = db.Column(db.Integer, db.ForeignKey('timesheet.id'), nullable=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    base_salary = db.Column(db.Float, default=0)
    hourly_wages = db.Column(db.Float, default=0)
    overtime_pay = db.Column(db.Float, default=0)
    bonuses = db.Column(db.Float, default=0)
    allowances = db.Column(db.Float, default=0)
    total_earnings = db.Column(db.Float, default=0)
    income_tax = db.Column(db.Float, default=0)
    loan_deduction = db.Column(db.Float, default=0)
    other_deductions = db.Column(db.Float, default=0)
    total_deductions = db.Column(db.Float, default=0)
    net_pay = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.Date)
    payment_reference = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    processed_by = db.Column(db.String(100))
    processed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='payments')
    timesheet = db.relationship('Timesheet', backref='payments')

# ============================================================================
# PRODUCTION/MANUFACTURING MODELS (PHASE 3)
# ============================================================================



class BatchRawMaterial(db.Model):
    """Track raw materials used in production batch"""
    __tablename__ = 'batch_raw_material'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batch.id'), nullable=False)
    material_name = db.Column(db.String(100), nullable=False)
    material_type = db.Column(db.String(50), nullable=True)
    quantity_used = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    cost_per_unit = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    supplier = db.Column(db.String(100), nullable=True)
    batch_code = db.Column(db.String(50), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class RawMaterialUsage(db.Model):
    """Track raw material usage in production"""
    __tablename__ = 'raw_material_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batch.id'), nullable=True)
    quantity_used = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    usage_date = db.Column(db.DateTime, default=datetime.utcnow)
    used_by = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

# ============================================================================
# PRODUCTION & BOM MODELS (ADD THESE AT END OF FILE)
# ============================================================================

class RawMaterial(db.Model):
    """Track raw materials (glass tubing, packaging, etc.)"""
    __tablename__ = 'raw_material'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    material_type = db.Column(db.String(50), nullable=True)  # Amber, Transparent
    specification = db.Column(db.String(200), nullable=True)
    current_stock = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20), nullable=False)  # meters, kg, pieces
    reorder_level = db.Column(db.Float, default=0)
    cost_per_unit = db.Column(db.Float, default=0)
    supplier = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BOMItem(db.Model):
    """Bill of Materials - Links products to raw materials"""
    __tablename__ = 'bom_item'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)  # e.g., 0.095 meters per ampoule
    unit = db.Column(db.String(20), nullable=False)
    waste_percentage = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Product (no backref to avoid conflict)
    product = db.relationship('Product', lazy=True)
    
    # Relationship to RawMaterial
    raw_material = db.relationship('RawMaterial', lazy=True)
    
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref
    # raw_material = db.relationship(...)  # Removed - created by parent backref


class MaterialUsage(db.Model):
    """Track raw material usage in production"""
    __tablename__ = 'material_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batch.id'), nullable=True)
    quantity_used = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    usage_type = db.Column(db.String(50), default='production')
    usage_date = db.Column(db.DateTime, default=datetime.utcnow)
    used_by = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)


class ProductionBatch(db.Model):
    """Track production batches"""
    __tablename__ = 'production_batch'
    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    planned_quantity = db.Column(db.Integer, nullable=False)
    actual_quantity = db.Column(db.Integer, nullable=True)
    rejected_quantity = db.Column(db.Integer, default=0)
    yield_percentage = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='planned')
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)  # ✅ ADD THIS LINE

class StockAlert(db.Model):
    """Track low stock alerts"""
    __tablename__ = 'stock_alert'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=True)
    threshold = db.Column(db.Integer, default=10000)
    current_stock = db.Column(db.Integer, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref
    material = db.relationship('RawMaterial', backref='stock_alerts', lazy=True)


class OrderApproval(db.Model):
    """Track order approvals for large orders"""
    __tablename__ = 'order_approval'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    requested_by = db.Column(db.String(100), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.String(100), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')
    rejection_reason = db.Column(db.Text, nullable=True)
    approval_threshold = db.Column(db.Float, nullable=False)
    
    # order = db.relationship(...)  # Removed - created by Order.order_items backref

    # ============================================================================
# SUPPLY CHAIN & PURCHASE MANAGEMENT MODELS (PHASE 5)
# ============================================================================

class Supplier(db.Model):
    """Supplier/Vendor database"""
    __tablename__ = 'supplier'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), default='Pakistan')
    cnic = db.Column(db.String(20), nullable=True)
    ntn = db.Column(db.String(20), nullable=True)
    payment_terms = db.Column(db.String(50), default='30 days')
    credit_limit = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    rating = db.Column(db.Float, default=5.0)  # 1-5 stars
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)


class PurchaseOrder(db.Model):
    """Purchase Orders for raw materials"""
    __tablename__ = 'purchase_order'
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)  # NEW
    expected_date = db.Column(db.DateTime, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, sent, received, cancelled
    total_amount = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    grand_total = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    paid_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True)
    goods_receipts = db.relationship('GoodsReceipt', backref='purchase_order', lazy=True)


class PurchaseOrderItem(db.Model):
    """Items in Purchase Order"""
    __tablename__ = 'purchase_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    quantity_ordered = db.Column(db.Float, nullable=False)
    quantity_received = db.Column(db.Float, default=0)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, default=0)
    tax_rate = db.Column(db.Float, default=17)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    
    # Relationships
    material = db.relationship('RawMaterial', backref='purchase_order_items', lazy=True)


class GoodsReceipt(db.Model):
    """Goods Receipt Note - Material inward"""
    __tablename__ = 'goods_receipt'
    
    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=True)
    receipt_date = db.Column(db.DateTime, default=datetime.utcnow)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, inspected, accepted, rejected
    total_items = db.Column(db.Integer, default=0)
    accepted_items = db.Column(db.Integer, default=0)
    rejected_items = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    received_by = db.Column(db.String(100), nullable=True)
    inspected_by = db.Column(db.String(100), nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    
    # Relationships
    items = db.relationship('GoodsReceiptItem', backref='goods_receipt', lazy=True)
    supplier = db.relationship('Supplier', backref='goods_receipts', lazy=True)


class GoodsReceiptItem(db.Model):
    """Items in Goods Receipt"""
    __tablename__ = 'goods_receipt_item'
    
    id = db.Column(db.Integer, primary_key=True)
    gr_id = db.Column(db.Integer, db.ForeignKey('goods_receipt.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    quantity_ordered = db.Column(db.Float, nullable=False)
    quantity_received = db.Column(db.Float, nullable=False)
    quantity_accepted = db.Column(db.Float, default=0)
    quantity_rejected = db.Column(db.Float, default=0)
    rejection_reason = db.Column(db.Text, nullable=True)
    batch_number = db.Column(db.String(50), nullable=True)
    manufacturing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    
    # Relationships
    material = db.relationship('RawMaterial', backref='goods_receipt_items', lazy=True)


class Warehouse(db.Model):
    """Warehouse/Storage Location"""
    __tablename__ = 'warehouse'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    manager = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stock_levels = db.relationship('WarehouseStock', backref='warehouse', lazy=True)
    goods_receipts = db.relationship('GoodsReceipt', backref='warehouse', lazy=True)


class WarehouseStock(db.Model):
    """Stock levels per warehouse"""
    __tablename__ = 'warehouse_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    quantity = db.Column(db.Float, default=0)
    reserved_quantity = db.Column(db.Float, default=0)
    available_quantity = db.Column(db.Float, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    material = db.relationship('RawMaterial', backref='warehouse_stocks', lazy=True)


class StockTransfer(db.Model):
    """Stock transfer between warehouses"""
    __tablename__ = 'stock_transfer'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_number = db.Column(db.String(50), unique=True, nullable=False)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, in_transit, completed, cancelled
    notes = db.Column(db.Text, nullable=True)
    requested_by = db.Column(db.String(100), nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    items = db.relationship('StockTransferItem', backref='stock_transfer', lazy=True)
    from_warehouse = db.relationship('Warehouse', foreign_keys=[from_warehouse_id], backref='outgoing_transfers')
    to_warehouse = db.relationship('Warehouse', foreign_keys=[to_warehouse_id], backref='incoming_transfers')


class StockTransferItem(db.Model):
    """Items in Stock Transfer"""
    __tablename__ = 'stock_transfer_item'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('stock_transfer.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    quantity_transferred = db.Column(db.Float, default=0)
    
    # Relationships
    material = db.relationship('RawMaterial', backref='stock_transfer_items', lazy=True)


class MaterialBatch(db.Model):
    """Track raw material batches with expiry"""
    __tablename__ = 'material_batch'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    quantity_received = db.Column(db.Float, nullable=False)
    quantity_used = db.Column(db.Float, default=0)
    quantity_remaining = db.Column(db.Float, default=0)
    manufacturing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, expired, consumed
    received_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    material = db.relationship('RawMaterial', backref='batches', lazy=True)
    supplier = db.relationship('Supplier', backref='material_batches', lazy=True)
    warehouse = db.relationship('Warehouse', backref='material_batches', lazy=True)


class SupplierInvoice(db.Model):
    """Supplier invoices for payment tracking"""
    __tablename__ = 'supplier_invoice'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=True)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    total_amount = db.Column(db.Float, default=0)
    paid_amount = db.Column(db.Float, default=0)
    balance_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid, overdue
    payment_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Supplier', backref='invoices', lazy=True)
    purchase_order = db.relationship('PurchaseOrder', backref='invoices', lazy=True)

    # ============================================================================
# QUALITY MANAGEMENT MODELS (PHASE 7)
# ============================================================================

class QCParameter(db.Model):
    """Quality Control Parameters for products"""
    __tablename__ = 'qc_parameter'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    parameter_name = db.Column(db.String(100), nullable=False)  # e.g., "Volume", "pH", "Clarity"
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    target_value = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    test_method = db.Column(db.String(200), nullable=True)
    is_mandatory = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref


class QCResult(db.Model):
    """Quality Control Test Results"""
    __tablename__ = 'qc_result'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('production_batch.id'), nullable=False)
    parameter_id = db.Column(db.Integer, db.ForeignKey('qc_parameter.id'), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    tested_value = db.Column(db.Float, nullable=True)
    result = db.Column(db.String(20), nullable=False)  # pass, fail, conditional
    tested_by = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    
    batch = db.relationship('ProductionBatch', backref='qc_results', lazy=True)
    parameter = db.relationship('QCParameter', backref='qc_results', lazy=True)


class CustomerComplaint(db.Model):
    """Customer Complaint Tracking"""
    __tablename__ = 'customer_complaint'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    batch_number = db.Column(db.String(50), nullable=True)
    complaint_date = db.Column(db.DateTime, default=datetime.utcnow)
    complaint_type = db.Column(db.String(50), nullable=True)  # Quality, Packaging, Delivery, Other
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='open')  # open, investigating, resolved, closed
    assigned_to = db.Column(db.String(100), nullable=True)
    investigation_notes = db.Column(db.Text, nullable=True)
    resolution = db.Column(db.Text, nullable=True)
    resolved_date = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.String(100), nullable=True)
    
    # customer = db.relationship(...)  # Removed - created by Customer.custom_prices backref
    # order = db.relationship(...)  # Removed - created by Order.order_items backref
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref


class CAPA(db.Model):
    """Corrective and Preventive Action"""
    __tablename__ = 'capa'
    
    id = db.Column(db.Integer, primary_key=True)
    capa_number = db.Column(db.String(50), unique=True, nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('customer_complaint.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # corrective, preventive
    root_cause = db.Column(db.Text, nullable=True)
    action_plan = db.Column(db.Text, nullable=False)
    assigned_to = db.Column(db.String(100), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, verified
    completion_date = db.Column(db.DateTime, nullable=True)
    effectiveness_check = db.Column(db.Text, nullable=True)
    closed_by = db.Column(db.String(100), nullable=True)
    closed_date = db.Column(db.DateTime, nullable=True)
    
    complaint = db.relationship('CustomerComplaint', backref='capa_records', lazy=True)


class CalibrationRecord(db.Model):
    """Equipment Calibration Records"""
    __tablename__ = 'calibration_record'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(100), nullable=False)
    equipment_id = db.Column(db.String(50), nullable=True)
    calibration_date = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date, nullable=False)
    calibration_result = db.Column(db.String(20), nullable=False)  # pass, fail, adjusted
    calibrated_by = db.Column(db.String(100), nullable=True)
    certificate_number = db.Column(db.String(50), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # ============================================================================
# ADVANCED INVENTORY MODELS (PHASE 8)
# ============================================================================

class StockMovement(db.Model):
    """Track all stock movements"""
    __tablename__ = 'stock_movement'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, adjustment, transfer
    quantity = db.Column(db.Float, nullable=False)
    reference_type = db.Column(db.String(50), nullable=True)  # PO, GRN, Production, Sale
    reference_id = db.Column(db.Integer, nullable=True)
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    
    material = db.relationship('RawMaterial', backref='stock_movements', lazy=True)
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref


class InventoryAdjustment(db.Model):
    """Stock adjustments with approval"""
    __tablename__ = 'inventory_adjustment'
    
    id = db.Column(db.Integer, primary_key=True)
    adjustment_number = db.Column(db.String(50), unique=True, nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    adjustment_type = db.Column(db.String(20), nullable=False)  # add, remove
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    requested_by = db.Column(db.String(100), nullable=True)
    requested_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.String(100), nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)
    
    material = db.relationship('RawMaterial', backref='adjustments', lazy=True)
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref


class StockCount(db.Model):
    """Physical stock count records"""
    __tablename__ = 'stock_count'
    
    id = db.Column(db.Integer, primary_key=True)
    count_number = db.Column(db.String(50), unique=True, nullable=False)
    count_date = db.Column(db.Date, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=True)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, verified
    counted_by = db.Column(db.String(100), nullable=True)
    verified_by = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    warehouse = db.relationship('Warehouse', backref='stock_counts', lazy=True)


class StockCountItem(db.Model):
    """Items in physical stock count"""
    __tablename__ = 'stock_count_item'
    
    id = db.Column(db.Integer, primary_key=True)
    count_id = db.Column(db.Integer, db.ForeignKey('stock_count.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    system_quantity = db.Column(db.Float, nullable=False)
    counted_quantity = db.Column(db.Float, nullable=False)
    variance = db.Column(db.Float, nullable=True)
    variance_reason = db.Column(db.Text, nullable=True)
    
    count = db.relationship('StockCount', backref='items', lazy=True)
    material = db.relationship('RawMaterial', backref='count_items', lazy=True)
    # product = db.relationship('Product')  # Removed - created by Product.orderitems backref

    # ============================================================================
# FBR TAX INTEGRATION MODELS (PHASE 9)
# ============================================================================

class FBRInvoice(db.Model):
    """FBR-compliant invoice tracking"""
    __tablename__ = 'fbr_invoice'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    fbr_invoice_number = db.Column(db.String(50), nullable=True)  # FBR assigned
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    taxable_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, nullable=False)
    withholding_tax = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='generated')  # generated, submitted, verified
    submitted_date = db.Column(db.DateTime, nullable=True)
    verified_date = db.Column(db.DateTime, nullable=True)
    
    # order = db.relationship(...)  # Removed - created by Order.order_items backref


class TaxReturn(db.Model):
    """Monthly tax return records"""
    __tablename__ = 'tax_return'
    
    id = db.Column(db.Integer, primary_key=True)
    return_period = db.Column(db.String(7), nullable=False)  # YYYY-MM
    sales_tax = db.Column(db.Float, default=0)
    input_tax = db.Column(db.Float, default=0)
    net_tax_payable = db.Column(db.Float, default=0)
    withholding_tax = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='draft')  # draft, filed, paid
    filed_date = db.Column(db.Date, nullable=True)
    payment_date = db.Column(db.Date, nullable=True)
    remarks = db.Column(db.Text, nullable=True)

# ============================================================================
# PAINTING SERVICE PRICING (NEW)
# ============================================================================

class PaintingServicePrice(db.Model):
    """Product-specific painting service prices"""
    __tablename__ = 'painting_service_price'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    minimum_quantity = db.Column(db.Integer, default=1000)
    setup_charge = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = db.relationship('Product', backref='painting_service_prices')


class PaintingOrder(db.Model):
    """Painting service orders"""
    __tablename__ = 'painting_order'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')
    total_amount = db.Column(db.Float, default=0)
    paid_amount = db.Column(db.Float, default=0)
    payment_status = db.Column(db.String(20), default='unpaid')
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    
    # customer = db.relationship(...)  # Removed - created by Customer.custom_prices backref
    items = db.relationship('PaintingOrderItem', backref='painting_order', lazy=True)


class PaintingOrderItem(db.Model):
    """Items in painting order"""
    __tablename__ = 'painting_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('painting_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    setup_charge = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, default=0)
    color_specification = db.Column(db.String(100), nullable=True)
    special_instructions = db.Column(db.Text, nullable=True)
    
    product = db.relationship('Product', backref='painting_order_items')


# ============================================================================
# CUSTOMER PAINTING PRICING (NEW)
# ============================================================================

class CustomerPaintingPrice(db.Model):
    """Customer-specific painting service prices"""
    __tablename__ = 'customer_painting_price'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    setup_charge = db.Column(db.Float, default=0)
    payment_terms = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # customer = db.relationship(...)  # Removed - created by Customer.custom_prices backref
    product = db.relationship('Product', backref='customer_painting_prices', lazy=True)    


# ============================================================================
# ACCOUNTING MODULE MODELS (ADD TO END OF models.py)
# ============================================================================

class Account(db.Model):
    """Chart of Accounts - Master account list"""
    __tablename__ = 'account'
    
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(20), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # Asset, Liability, Equity, Income, Expense
    parent_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships (no backref to avoid conflicts)
    parent = db.relationship('Account', remote_side=[id], backref='sub_accounts', lazy=True)
    journal_lines = db.relationship('JournalEntryLine', backref='account', lazy=True)
    payment_voucher_lines = db.relationship('PaymentVoucherLine', backref='account', lazy=True)
    receipt_voucher_lines = db.relationship('ReceiptVoucherLine', backref='account', lazy=True)


class JournalEntry(db.Model):
    """Journal Entries - Double-entry accounting records"""
    __tablename__ = 'journal_entry'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    reference = db.Column(db.String(100))  # Invoice #, PO #, etc.
    reference_type = db.Column(db.String(50))  # invoice, payment, receipt, adjustment
    reference_id = db.Column(db.Integer)  # ID of referenced document
    status = db.Column(db.String(20), default='draft')  # draft, posted, cancelled
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posted_by = db.Column(db.String(100))
    posted_at = db.Column(db.DateTime)
    
    # Relationship
    lines = db.relationship('JournalEntryLine', backref='entry', lazy=True)


class JournalEntryLine(db.Model):
    """Journal Entry Lines - Debit/Credit entries"""
    __tablename__ = 'journal_entry_line'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    description = db.Column(db.String(200))
    debit = db.Column(db.Float, default=0)
    credit = db.Column(db.Float, default=0)


class AccountingPeriod(db.Model):
    """Accounting Periods for month-end closing"""
    __tablename__ = 'accounting_period'
    
    id = db.Column(db.Integer, primary_key=True)
    period_name = db.Column(db.String(50), nullable=False)  # e.g., "March 2026"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    closed_by = db.Column(db.String(100))
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BankAccount(db.Model):
    """Bank Accounts for reconciliation"""
    __tablename__ = 'bank_account'
    
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    bank_name = db.Column(db.String(100))
    account_type = db.Column(db.String(50), default='current')
    opening_balance = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reconciliations = db.relationship('BankReconciliation', backref='bank_account', lazy=True)
    payment_vouchers = db.relationship('PaymentVoucher', backref='bank_account', lazy=True)
    receipt_vouchers = db.relationship('ReceiptVoucher', backref='bank_account', lazy=True)


class BankReconciliation(db.Model):
    """Bank Reconciliation Records"""
    __tablename__ = 'bank_reconciliation'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    reconciliation_date = db.Column(db.Date, nullable=False)
    statement_balance = db.Column(db.Float, nullable=False)
    book_balance = db.Column(db.Float, nullable=False)
    outstanding_deposits = db.Column(db.Float, default=0)
    outstanding_checks = db.Column(db.Float, default=0)
    adjusted_balance = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    prepared_by = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PaymentVoucher(db.Model):
    """Payment Vouchers for cash/bank payments"""
    __tablename__ = 'payment_voucher'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(50), unique=True, nullable=False)
    voucher_date = db.Column(db.Date, nullable=False)
    payee_name = db.Column(db.String(100), nullable=False)
    payee_type = db.Column(db.String(50))  # supplier, employee, other
    payee_id = db.Column(db.Integer)  # ID of supplier/employee
    payment_method = db.Column(db.String(50), default='cash')
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=True)
    cheque_number = db.Column(db.String(50))
    total_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    approved_by = db.Column(db.String(100))
    paid_by = db.Column(db.String(100))
    paid_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lines = db.relationship('PaymentVoucherLine', backref='voucher', lazy=True)


class PaymentVoucherLine(db.Model):
    """Payment Voucher Lines"""
    __tablename__ = 'payment_voucher_line'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('payment_voucher.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)


class ReceiptVoucher(db.Model):
    """Receipt Vouchers for cash/bank receipts"""
    __tablename__ = 'receipt_voucher'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(50), unique=True, nullable=False)
    voucher_date = db.Column(db.Date, nullable=False)
    payer_name = db.Column(db.String(100), nullable=False)
    payer_type = db.Column(db.String(50))  # customer, other
    payer_id = db.Column(db.Integer)  # ID of customer
    payment_method = db.Column(db.String(50), default='cash')
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=True)
    cheque_number = db.Column(db.String(50))
    total_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    received_by = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lines = db.relationship('ReceiptVoucherLine', backref='voucher', lazy=True)


class ReceiptVoucherLine(db.Model):
    """Receipt Voucher Lines"""
    __tablename__ = 'receipt_voucher_line'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('receipt_voucher.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)


class FixedAsset(db.Model):
    """Fixed assets: machinery, furnaces, vehicles, equipment"""
    __tablename__ = 'fixed_asset'

    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)   # Machinery, Furniture, Vehicle, Building, IT Equipment
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    supplier = db.Column(db.String(150))
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_cost = db.Column(db.Float, nullable=False)
    useful_life_years = db.Column(db.Integer, default=5)
    depreciation_method = db.Column(db.String(20), default='straight_line')  # straight_line / reducing_balance
    salvage_value = db.Column(db.Float, default=0)
    accumulated_depreciation = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='active')   # active, disposed, under_maintenance
    disposal_date = db.Column(db.Date)
    disposal_value = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def book_value(self):
        return max(0, self.purchase_cost - self.accumulated_depreciation)

    @property
    def annual_depreciation(self):
        if self.depreciation_method == 'straight_line':
            return (self.purchase_cost - self.salvage_value) / max(1, self.useful_life_years)
        return 0

    @property
    def monthly_depreciation(self):
        return self.annual_depreciation / 12


class Shift(db.Model):
    """Work shifts for 24/7 glass manufacturing"""
    __tablename__ = 'shift'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    shift_type = db.Column(db.String(20), default='day')  # day / evening / night
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM
    end_time = db.Column(db.String(5), nullable=False)    # HH:MM
    duration_hours = db.Column(db.Float, default=8)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignments = db.relationship('ShiftAssignment', backref='shift', lazy=True)


class ShiftAssignment(db.Model):
    """Assigns employees to shifts for a date range"""
    __tablename__ = 'shift_assignment'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=False)
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date)          # NULL = indefinite
    notes = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', backref='shift_assignments')


class AuditLog(db.Model):
    """Audit Trail for all accounting changes"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def created_at(self):
        return self.timestamp