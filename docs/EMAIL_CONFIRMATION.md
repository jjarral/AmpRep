# Inquiry email confirmation

The public form confirms inbox access with a six-digit code. Syntax and DNS checks
are preliminary checks; only a correct code allows a confirmed inquiry.

## Activation

1. Connect the `resend/resend-email` Vercel integration on its **Free** plan for
   the sending domain `notify.ampoulex.com`. Keep paid overages disabled.
2. Add the exact verification DNS records supplied by Resend at the domain's
   authoritative DNS provider. Wait for Resend to report the domain as verified.
3. Set these production environment variables in Vercel:
   - `RESEND_API_KEY`: the integration's sending API key (never commit this).
   - `EMAIL_FROM`: `Ampoulex <confirmation@notify.ampoulex.com>`.
   - `INQUIRY_EMAIL_VERIFICATION_REQUIRED`: `true`.
4. Redeploy. Complete a real inbox confirmation before treating mail delivery as
   verified. Do not enable the requirement while the sender is unconfigured.

The feature flag defaults off so connecting a provider cannot interrupt existing
inquiries midway through setup. When enabled, missing sender configuration fails
closed and the server refuses inquiries without a confirmed code.

## Controls

- Codes expire after 10 minutes; a successful confirmation lasts 30 minutes.
- Confirmation is bound to the email address and browser session.
- Five incorrect attempts lock a code. Resends invalidate previous codes.
- A confirmation is consumed in the same transaction as the saved inquiry.
- CSRF checks protect sending, confirmation, and final inquiry submission.
- Database counters limit requests across all Vercel instances: 3 per inbox/hour,
  6 per browser/hour, 12 per IP/hour, and 90 total emails/day (at most 2,790 in a
  31-day month). A 60-second resend pause also applies.
- Codes are HMAC hashed, never stored in plaintext, returned by the API or logged.
- Expired verification records are removed after a day on subsequent send requests.
- No customer record is created until the inquiry passes confirmation and validation.

Staff access remains available directly at `/login` and `/dashboard`. The public
footer has no staff login link.

## Checks

Run `python -m unittest discover -s tests -v` with the repository's Flask,
SQLAlchemy and email-validator dependencies available. Tests use an in-memory
SQLite database and mock sending and DNS; they do not prove live mail delivery.
