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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specification = db.Column(db.String(200))
    base_price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    color = db.Column(db.String(20))
    product_type = db.Column(db.String(20), default='product')
    material_type = db.Column(db.String(50))
    usp_type = db.Column(db.String(50))
    shape_type = db.Column(db.String(50))
    dimensions = db.Column(db.String(100))
    use_case = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    
    custom_prices = db.relationship('CustomerProductPrice', back_populates='customer', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', back_populates='customer', lazy=True)

class CustomerProductPrice(db.Model):
    __tablename__ = 'customer_product_price'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    agreed_price = db.Column(db.Float, nullable=False)
    payment_terms = db.Column(db.String(50))
    
    customer = db.relationship('Customer', back_populates='custom_prices')
    product = db.relationship('Product')

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
    
    inquiry_items = db.relationship('InquiryItem', back_populates='parent_inquiry', lazy=True, cascade='all, delete-orphan')
    product = db.relationship('Product', foreign_keys=[product_id])

class InquiryItem(db.Model):
    __tablename__ = 'inquiry_item'
    id = db.Column(db.Integer, primary_key=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiry.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parent_inquiry = db.relationship('Inquiry', back_populates='inquiry_items')
    product = db.relationship('Product')

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
    
    customer = db.relationship('Customer', back_populates='orders')
    inquiry = db.relationship('Inquiry')
    order_items = db.relationship('OrderItem', back_populates='parent_order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    parent_order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product')

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
    
    product = db.relationship('Product')

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
    
    product = db.relationship('Product', backref='bom_items', lazy=True)
    raw_material = db.relationship('RawMaterial', backref='bom_items', lazy=True)


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
    
    product = db.relationship('Product', backref='production_batches', lazy=True)


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
    
    product = db.relationship('Product', backref='stock_alerts', lazy=True)
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
    
    order = db.relationship('Order', backref='approval_request', lazy=True)

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
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # NEW
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