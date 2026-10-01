"""Confirm possession of an email inbox before accepting a public inquiry."""
from datetime import datetime, timedelta
import calendar
import hashlib
import hmac
import json
import re
import secrets
import urllib.error
import urllib.request

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, current_app, jsonify, request, session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app import db
from app.models import EmailVerificationRate, InquiryEmailChallenge

email_verification_bp = Blueprint('inquiry_email', __name__)


class VerificationError(Exception):
    def __init__(self, message, status=400, retry_after=None):
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after


def enabled():
    return current_app.config.get('INQUIRY_EMAIL_VERIFICATION_REQUIRED', False)


def form_context():
    if not enabled():
        return {'enabled': False}
    if 'inquiry_email_session' not in session:
        session['inquiry_email_session'] = secrets.token_urlsafe(32)
    if 'inquiry_email_csrf' not in session:
        session['inquiry_email_csrf'] = secrets.token_urlsafe(32)
    return {'enabled': True, 'csrf': session['inquiry_email_csrf']}


def digest(value):
    return hmac.new(current_app.secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()


def session_digest():
    token = session.get('inquiry_email_session')
    if not token:
        raise VerificationError('Refresh the page before confirming your email.', 403)
    return digest('session:' + token)


def check_csrf(value):
    expected = session.get('inquiry_email_csrf', '')
    if not expected or not isinstance(value, str) or not hmac.compare_digest(expected, value):
        raise VerificationError('Your page has expired. Refresh it and try again.', 403)


def checked_email(value, check_dns=False):
    if not isinstance(value, str) or len(value.strip()) > 120:
        raise VerificationError('Enter a valid email address.')
    try:
        result = validate_email(value.strip(), check_deliverability=check_dns,
                                allow_smtputf8=False, timeout=4)
    except EmailNotValidError as exc:
        raise VerificationError(str(exc)) from exc
    if check_dns and result.as_dict().get('unknown-deliverability'):
        raise VerificationError('We could not check your email provider. Please try again shortly.', 503)
    return result.normalized.lower()


def consume_limit(kind, identity, seconds, maximum, now):
    """Atomic upsert prevents concurrent serverless requests exceeding the limit."""
    timestamp = calendar.timegm(now.utctimetuple())
    window = timestamp // seconds
    key = digest(f'{kind}:{identity}:{window}')
    expiry = datetime.utcfromtimestamp((window + 1) * seconds)
    values = {'key': key, 'count': 1, 'expires_at': expiry}
    insert = pg_insert if db.engine.dialect.name == 'postgresql' else sqlite_insert
    statement = insert(EmailVerificationRate).values(**values)
    statement = statement.on_conflict_do_update(
        index_elements=['key'], set_={'count': EmailVerificationRate.count + 1}
    ).returning(EmailVerificationRate.count)
    count = db.session.execute(statement).scalar_one()
    if count > maximum:
        wait = max(1, int((expiry - now).total_seconds()) + 1)
        raise VerificationError('Too many confirmation requests. Please try again later.', 429, wait)


def send_code_email(email, code, challenge_id):
    api_key = current_app.config.get('RESEND_API_KEY')
    sender = current_app.config.get('EMAIL_FROM')
    if not api_key or not sender:
        raise VerificationError('Email confirmation is temporarily unavailable. Please contact info@ampoulex.com.', 503)
    message = {
        'from': sender,
        'to': [email],
        'subject': 'Confirm your email for your Ampoulex inquiry',
        'text': f'Your Ampoulex confirmation code is {code}.\n\n'
                'Enter this code on the inquiry form. It expires in 10 minutes. '
                'Do not share this code.\n\n'
                'If you did not request this code, you can ignore this email.\n\nAmpoulex',
    }
    req = urllib.request.Request('https://api.resend.com/emails',
        data=json.dumps(message).encode(), method='POST', headers={
            'Authorization': 'Bearer ' + api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Ampoulex/1.0',
            'Idempotency-Key': 'inquiry-confirmation/' + challenge_id,
        })
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = json.load(response)
            if not payload.get('id'):
                raise ValueError('Missing provider receipt')
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        # Provider response bodies may contain addresses: keep them out of logs.
        current_app.logger.warning('Inquiry confirmation email could not be sent (%s)', type(exc).__name__)
        raise VerificationError('We could not send your code. Please try again in a minute.', 503, 60) from exc


def json_input():
    if not enabled():
        raise VerificationError('Email confirmation is not available yet.', 503)
    if request.content_length and request.content_length > 4096:
        raise VerificationError('Request is too large.', 413)
    check_csrf(request.headers.get('X-Verification-CSRF', ''))
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise VerificationError('Please enter your email address.')
    return data


@email_verification_bp.errorhandler(VerificationError)
def verification_error(error):
    db.session.rollback()
    response = jsonify({'ok': False, 'message': str(error), 'retry_after': error.retry_after})
    response.status_code = error.status
    if error.retry_after:
        response.headers['Retry-After'] = str(error.retry_after)
    return response


@email_verification_bp.after_request
def prevent_caching(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@email_verification_bp.route('/inquiry-email/send-code', methods=['POST'])
def send_code():
    data = json_input()
    if not current_app.config.get('RESEND_API_KEY') or not current_app.config.get('EMAIL_FROM'):
        raise VerificationError('Email confirmation is temporarily unavailable. Please contact info@ampoulex.com.', 503)
    email = checked_email(data.get('email', ''))
    browser = session_digest()
    now = datetime.utcnow()
    # Lock-free atomic counters bound abuse and stay below Resend's free limits.
    consume_limit('global-day', 'site', 86400, 90, now)
    consume_limit('ip-hour', request.remote_addr or 'unknown', 3600, 12, now)
    consume_limit('session-hour', browser, 3600, 6, now)
    consume_limit('email-hour', email, 3600, 3, now)
    consume_limit('email-minute', email, 60, 1, now)
    consume_limit('session-minute', browser, 60, 1, now)
    # Commit rate limits even when the provider or DNS later fails.
    db.session.commit()
    email = checked_email(email, check_dns=True)
    now = datetime.utcnow()
    # Verification tokens are temporary; retain only a short troubleshooting window.
    InquiryEmailChallenge.query.filter(
        InquiryEmailChallenge.expires_at < now - timedelta(days=1)
    ).delete(synchronize_session=False)
    EmailVerificationRate.query.filter(
        EmailVerificationRate.expires_at < now
    ).delete(synchronize_session=False)
    previous = InquiryEmailChallenge.query.filter_by(email=email).order_by(
        InquiryEmailChallenge.created_at.desc()).first()
    if previous and (now - previous.created_at).total_seconds() < 60:
        raise VerificationError('Please wait a minute before requesting another code.', 429, 60)
    challenge_id = secrets.token_urlsafe(32)
    code = f'{secrets.randbelow(1_000_000):06d}'
    challenge = InquiryEmailChallenge(id=challenge_id, email=email, session_digest=browser, created_at=now,
        code_digest=digest(f'code:{challenge_id}:{code}'), expires_at=now + timedelta(minutes=10))
    # A resend supersedes earlier codes for this inbox and browser.
    InquiryEmailChallenge.query.filter_by(email=email, session_digest=browser, consumed_at=None).update(
        {'expires_at': now}, synchronize_session=False)
    db.session.add(challenge)
    db.session.commit()
    send_code_email(email, code, challenge_id)
    challenge.sent = True
    db.session.commit()
    return jsonify({'ok': True, 'challenge_id': challenge_id, 'expires_in': 600,
                    'retry_after': 60, 'message': 'Code sent. Check your inbox and spam folder.'})


def get_challenge(challenge_id, email):
    if not isinstance(challenge_id, str) or len(challenge_id) > 64:
        raise VerificationError('Request a new confirmation code.')
    challenge = InquiryEmailChallenge.query.filter_by(id=challenge_id).with_for_update().first()
    now = datetime.utcnow()
    if (not challenge or not challenge.sent or challenge.email != email
            or not hmac.compare_digest(challenge.session_digest, session_digest())
            or challenge.consumed_at or challenge.expires_at <= now):
        raise VerificationError('Your confirmation has expired or does not match this email. Request a new code.')
    return challenge


@email_verification_bp.route('/inquiry-email/confirm', methods=['POST'])
def confirm_code():
    data = json_input()
    email = checked_email(data.get('email', ''))
    challenge = get_challenge(data.get('challenge_id', ''), email)
    if challenge.attempts >= 5:
        raise VerificationError('Too many incorrect codes. Request a new code.', 429)
    code = data.get('code', '')
    if (not isinstance(code, str) or not re.fullmatch(r'[0-9]{6}', code)
            or not hmac.compare_digest(challenge.code_digest, digest(f'code:{challenge.id}:{code}'))):
        challenge.attempts += 1
        db.session.commit()
        raise VerificationError('That code is incorrect. Check the email and try again.')
    if not challenge.verified_at:
        challenge.verified_at = datetime.utcnow()
        challenge.expires_at = challenge.verified_at + timedelta(minutes=30)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'Email confirmed. You can now send your inquiry.'})


def consume_confirmation(email, challenge_id, csrf):
    """Consumed in the same transaction as the inquiry so a proof cannot be replayed."""
    check_csrf(csrf)
    challenge = get_challenge(challenge_id, checked_email(email))
    if not challenge.verified_at:
        raise VerificationError('Confirm your email using the code before sending your inquiry.')
    challenge.consumed_at = datetime.utcnow()
    return challenge.verified_at
