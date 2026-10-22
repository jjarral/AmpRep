"""Admin workflow tests. Run: python -m unittest discover tests
All data stays in an in-memory SQLite database; nothing touches ampoulex.db or production."""
from datetime import datetime, timedelta
from pathlib import Path
import unittest
from unittest.mock import patch

from flask import Flask

from app import db, login_manager
from app.inquiry_email import email_verification_bp, form_context
from app.models import User, Customer, Order, CustomerPayment, PaymentVoucher
from app.routes import main_bp


class AdminWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder=str(Path(__file__).parents[1] / 'templates'),
                         static_folder=str(Path(__file__).parents[1] / 'static'))
        self.app.config.update(TESTING=True, SECRET_KEY='isolated-test-key',
                               SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        db.init_app(self.app)
        login_manager.init_app(self.app)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(email_verification_bp)
        self.app.jinja_env.globals['inquiry_email_context'] = form_context
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        patch('app.routes.socketio.emit').start()
        self.addCleanup(patch.stopall)
        user = User(username='tester', email='tester@example.test', role='admin')
        user.set_password('pass-for-tests-only')
        db.session.add(user)
        db.session.commit()
        self.client = self.app.test_client()
        self.client.post('/login', data={'username': 'tester', 'password': 'pass-for-tests-only'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def make_order(self, total=100000, paid=0, status='processing', days_ago=40, terms='30 days'):
        customer = Customer.query.first() or Customer(name='Ali', business_name='Test Pharma',
                                                      email='ali@example.test', payment_terms=terms)
        db.session.add(customer)
        db.session.flush()
        order = Order(order_number=f'ORD-T{Order.query.count() + 1}', customer_id=customer.id,
                      total_amount=total, paid_amount=paid, status=status,
                      payment_status='unpaid' if not paid else 'partial',
                      customer_name_snapshot='Ali', customer_business_snapshot='Test Pharma',
                      created_at=datetime.utcnow() - timedelta(days=days_ago))
        db.session.add(order)
        db.session.commit()
        return order

    # --- blank optional numbers must not crash forms -------------------------------
    def test_customer_add_with_blank_credit_limit_saves(self):
        r = self.client.post('/customers/add', data={'name': 'Blank Limit', 'credit_limit': '',
                                                      'email': 'blank@example.test'}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(Customer.query.filter_by(name='Blank Limit').first())

    def test_payment_voucher_with_blank_bank_account_saves(self):
        r = self.client.post('/accounting/payment-vouchers/add', data={
            'payee_name': 'Glass supplier', 'payment_method': 'cash', 'bank_account_id': '',
            'voucher_date': datetime.utcnow().date().isoformat()}, follow_redirects=True)
        self.assertNotIn(b'invalid literal', r.data)
        self.assertEqual(PaymentVoucher.query.count(), 1)

    # --- database errors are explained, not dumped ------------------------------------
    def test_duplicate_customer_email_shows_plain_message(self):
        self.client.post('/customers/add', data={'name': 'First', 'email': 'dup@example.test'})
        r = self.client.post('/customers/add', data={'name': 'Second', 'email': 'dup@example.test'},
                             follow_redirects=True)
        self.assertNotIn(b'IntegrityError', r.data)
        self.assertNotIn(b'[SQL:', r.data)
        self.assertEqual(Customer.query.filter_by(email='dup@example.test').count(), 1)

    # --- receivables ---------------------------------------------------------------
    def test_partial_payment_updates_order(self):
        order = self.make_order(total=100000)
        r = self.client.post(f'/orders/{order.id}/payments', data={
            'amount': '40000', 'paid_on': datetime.utcnow().date().isoformat(), 'method': 'bank',
            'reference': 'TXN-1', 'next': '/receivables'}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        db.session.refresh(order)
        self.assertEqual(order.paid_amount, 40000)
        self.assertEqual(order.payment_status, 'partial')
        self.assertEqual(CustomerPayment.query.count(), 1)

    def test_full_payment_marks_order_paid(self):
        order = self.make_order(total=50000, paid=10000)
        self.client.post(f'/orders/{order.id}/payments', data={'amount': '40000', 'method': 'cash'})
        db.session.refresh(order)
        self.assertEqual(order.payment_status, 'paid')

    def test_overpayment_is_rejected(self):
        order = self.make_order(total=50000)
        r = self.client.post(f'/orders/{order.id}/payments', data={'amount': '999999', 'method': 'bank'},
                             follow_redirects=True)
        db.session.refresh(order)
        self.assertEqual(order.paid_amount, 0)
        self.assertEqual(CustomerPayment.query.count(), 0)
        self.assertIn(b'still owed', r.data)

    def test_cancelled_order_cannot_take_payment(self):
        order = self.make_order(status='cancelled')
        self.client.post(f'/orders/{order.id}/payments', data={'amount': '100', 'method': 'bank'})
        self.assertEqual(CustomerPayment.query.count(), 0)

    def test_removing_payment_restores_balance(self):
        order = self.make_order(total=100000)
        self.client.post(f'/orders/{order.id}/payments', data={'amount': '30000', 'method': 'bank'})
        payment = CustomerPayment.query.first()
        self.client.post(f'/payments/{payment.id}/delete', data={'confirm': 'on'})
        db.session.refresh(order)
        self.assertEqual(order.paid_amount, 0)
        self.assertEqual(order.payment_status, 'unpaid')
        self.assertEqual(CustomerPayment.query.count(), 0)

    def test_order_with_payments_cannot_be_deleted(self):
        order = self.make_order(total=100000)
        self.client.post(f'/orders/{order.id}/payments', data={'amount': '1000', 'method': 'bank'})
        self.client.post(f'/orders/delete/{order.id}')
        self.assertIsNotNone(db.session.get(Order, order.id))

    def test_receivables_aging_buckets(self):
        self.make_order(total=100000, days_ago=40)   # 30-day terms -> 10 days late
        self.make_order(total=20000, days_ago=5)     # not yet due
        r = self.client.get('/receivables')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'120,000', r.data)          # total owed
        self.assertIn(b'10 days late', r.data)

    def test_customer_statement_running_balance(self):
        order = self.make_order(total=100000)
        self.client.post(f'/orders/{order.id}/payments', data={'amount': '25000', 'method': 'bank'})
        r = self.client.get(f'/receivables/customer/{order.customer_id}')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'PKR 75,000', r.data)

    def test_dashboard_renders_with_orders(self):
        self.make_order(total=100000, days_ago=2)
        r = self.client.get('/dashboard')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'To collect', r.data)

    # --- audit fixes ------------------------------------------------------------------
    def test_statement_rows_do_not_use_framework_invoice_class(self):
        order = self.make_order(total=100000)
        r = self.client.get(f'/receivables/customer/{order.customer_id}')
        self.assertNotIn(b'<tr class="invoice"', r.data)  # AdminLTE paints .invoice white

    def test_login_ignores_external_next_url(self):
        self.client.get('/logout')
        r = self.client.post('/login?next=https://evil.example/phish',
                             data={'username': 'tester', 'password': 'pass-for-tests-only'})
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('evil.example', r.headers['Location'])

    def test_login_keeps_internal_next_url(self):
        self.client.get('/logout')
        r = self.client.post('/login?next=/receivables',
                             data={'username': 'tester', 'password': 'pass-for-tests-only'})
        self.assertTrue(r.headers['Location'].endswith('/receivables'))

    def test_delete_by_plain_link_is_refused(self):
        customer = Customer(name='Keep Me', email='keep@example.test')
        db.session.add(customer)
        db.session.commit()
        r = self.client.get(f'/customers/delete/{customer.id}')
        self.assertEqual(r.status_code, 405)
        self.assertIsNotNone(db.session.get(Customer, customer.id))

    def test_customer_bulk_upload_page_opens(self):
        self.assertEqual(self.client.get('/customers/bulk-upload').status_code, 200)


if __name__ == '__main__':
    unittest.main()
