"""Run with unittest; all data stays in SQLite memory and emails are mocked."""
from datetime import datetime, timedelta
from pathlib import Path
import unittest
from unittest.mock import patch

from email_validator import validate_email as real_validate_email
from flask import Flask

from app import db, login_manager
from app.inquiry_email import email_verification_bp, form_context, VerificationError
from app.models import Inquiry, InquiryEmailChallenge
from app.routes import main_bp


class InquiryEmailTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder=str(Path(__file__).parents[1] / 'templates'))
        self.app.config.update(TESTING=True, SECRET_KEY='isolated-test-key',
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            INQUIRY_EMAIL_VERIFICATION_REQUIRED=True,
            RESEND_API_KEY='test-only', EMAIL_FROM='Ampoulex <confirm@example.com>')
        db.init_app(self.app)
        login_manager.init_app(self.app)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(email_verification_bp)
        self.app.jinja_env.globals['inquiry_email_context'] = form_context
        self.app.add_url_rule('/test-context', 'test_context', lambda: form_context())
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.csrf = self.client.get('/test-context').json['csrf']
        self.sender = patch('app.inquiry_email.send_code_email').start()
        patch('app.routes.socketio.emit').start()
        patch('app.inquiry_email.validate_email', side_effect=lambda value, **kwargs:
              real_validate_email(value, check_deliverability=False, allow_smtputf8=False)).start()
        self.addCleanup(patch.stopall)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def send(self, email='buyer@example.com', client=None, csrf=None):
        return (client or self.client).post('/inquiry-email/send-code',
            json={'email': email}, headers={'X-Verification-CSRF': csrf or self.csrf})

    def sent(self):
        response = self.send()
        self.assertEqual(response.status_code, 200, response.json)
        email, code, identifier = self.sender.call_args.args
        self.assertEqual(response.json['challenge_id'], identifier)
        return identifier, code

    def confirm(self, identifier, code, email='buyer@example.com', client=None, csrf=None):
        return (client or self.client).post('/inquiry-email/confirm',
            json={'email': email, 'challenge_id': identifier, 'code': code},
            headers={'X-Verification-CSRF': csrf or self.csrf})

    def submit(self, identifier='', email='buyer@example.com', csrf=None):
        return self.client.post('/submit-inquiry', data={
            'customer_name': 'Sample Buyer', 'business_name': 'Sample Glass',
            'email': email, 'phone': '+923001234567',
            'product_options': 'clear', 'option_qty_clear': '1000',
            'email_challenge_id': identifier, 'email_verification_csrf': csrf or self.csrf})

    def test_confirmed_inbox_can_submit_once(self):
        identifier, code = self.sent()
        self.assertEqual(self.confirm(identifier, code).status_code, 200)
        self.assertEqual(self.submit(identifier).status_code, 302)
        self.assertEqual(Inquiry.query.count(), 1)
        self.assertIn('Email inbox confirmed:', Inquiry.query.one().notes)
        self.submit(identifier)
        self.assertEqual(Inquiry.query.count(), 1)

    def test_cannot_bypass_confirmation_with_direct_post(self):
        self.submit()
        self.assertEqual(Inquiry.query.count(), 0)

    def test_sent_but_unconfirmed_is_not_accepted(self):
        identifier, _ = self.sent()
        self.submit(identifier)
        self.assertEqual(Inquiry.query.count(), 0)

    def test_confirmed_proof_cannot_be_used_for_changed_address(self):
        identifier, code = self.sent()
        self.confirm(identifier, code)
        self.submit(identifier, email='different@example.com')
        self.assertEqual(Inquiry.query.count(), 0)

    def test_wrong_codes_lock_after_five_attempts(self):
        identifier, code = self.sent()
        wrong = '000001' if code == '000000' else '000000'
        for _ in range(5):
            self.assertEqual(self.confirm(identifier, wrong).status_code, 400)
        self.assertEqual(self.confirm(identifier, code).status_code, 429)
        self.assertIsNone(db.session.get(InquiryEmailChallenge, identifier).verified_at)

    def test_expired_code_is_rejected(self):
        identifier, code = self.sent()
        db.session.get(InquiryEmailChallenge, identifier).expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        self.assertEqual(self.confirm(identifier, code).status_code, 400)

    def test_expired_confirmation_cannot_submit(self):
        identifier, code = self.sent()
        self.confirm(identifier, code)
        db.session.get(InquiryEmailChallenge, identifier).expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        self.submit(identifier)
        self.assertEqual(Inquiry.query.count(), 0)

    def test_code_bound_to_browser_session(self):
        identifier, code = self.sent()
        other = self.app.test_client()
        other_csrf = other.get('/test-context').json['csrf']
        response = self.confirm(identifier, code, client=other, csrf=other_csrf)
        self.assertEqual(response.status_code, 400)

    def test_csrf_is_required_for_send_confirm_and_submit(self):
        self.assertEqual(self.send(csrf='wrong').status_code, 403)
        self.sender.assert_not_called()
        identifier, code = self.sent()
        self.assertEqual(self.confirm(identifier, code, csrf='wrong').status_code, 403)
        self.confirm(identifier, code)
        self.submit(identifier, csrf='wrong')
        self.assertEqual(Inquiry.query.count(), 0)

    def test_resend_rate_limit(self):
        self.sent()
        self.assertEqual(self.send().status_code, 429)
        self.assertEqual(self.sender.call_count, 1)

    def test_invalid_address_does_not_send(self):
        self.assertEqual(self.send('not-an-email').status_code, 400)
        self.sender.assert_not_called()

    def test_dns_uncertainty_is_not_reported_as_confirmation(self):
        uncertain = real_validate_email('buyer@example.com', check_deliverability=False)
        setattr(uncertain, 'unknown-deliverability', 'timeout')
        with patch('app.inquiry_email.validate_email', return_value=uncertain):
            self.assertEqual(self.send().status_code, 503)
        self.sender.assert_not_called()

    def test_disabled_feature_does_not_send_email(self):
        self.app.config['INQUIRY_EMAIL_VERIFICATION_REQUIRED'] = False
        self.assertEqual(self.send().status_code, 503)
        self.sender.assert_not_called()

    def test_provider_failure_does_not_create_valid_confirmation(self):
        self.sender.side_effect = VerificationError('Service unavailable', 503)
        self.assertEqual(self.send().status_code, 503)
        self.assertFalse(InquiryEmailChallenge.query.one().sent)

    def test_missing_sender_is_not_silently_bypassed(self):
        self.app.config['RESEND_API_KEY'] = ''
        self.assertEqual(self.send().status_code, 503)
        self.submit()
        self.assertEqual(Inquiry.query.count(), 0)

    def test_plain_code_not_stored_or_returned(self):
        identifier, code = self.sent()
        challenge = db.session.get(InquiryEmailChallenge, identifier)
        self.assertNotEqual(challenge.code_digest, code)
        self.assertEqual(len(challenge.code_digest), 64)


if __name__ == '__main__':
    unittest.main()
