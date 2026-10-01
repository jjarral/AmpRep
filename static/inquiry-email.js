(() => {
  'use strict';
  const panel = document.getElementById('email-confirmation');
  if (!panel) return;
  const form = document.getElementById('quote-form');
  const email = document.getElementById('contact-email');
  const send = document.getElementById('send-email-code');
  const confirm = document.getElementById('confirm-email-code');
  const code = document.getElementById('email-code');
  const fields = document.getElementById('email-code-fields');
  const status = document.getElementById('email-confirmation-status');
  const challenge = document.getElementById('email-challenge-id');
  const csrf = form.elements.email_verification_csrf.value;
  let confirmedEmail = '';
  let codeEmail = '';
  let cooldownUntil = 0;
  let busy = false;
  let revision = 0;
  const normalizedEmail = () => email.value.trim().toLowerCase();
  const updateSendButton = () => {
    const seconds = Math.max(0, Math.ceil((cooldownUntil - Date.now()) / 1000));
    send.disabled = busy || seconds > 0 || Boolean(confirmedEmail);
    send.textContent = confirmedEmail ? 'Email confirmed ✓' : busy ? 'Please wait…'
      : seconds > 0 ? `Resend in ${seconds}s` : codeEmail ? 'Resend code' : 'Send confirmation code';
    confirm.disabled = busy;
  };
  const message = (text, error = false) => {
    status.textContent = text;
    status.classList.toggle('input-error', error);
  };
  async function post(url, data) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(url, {
        method: 'POST', credentials: 'same-origin', signal: controller.signal,
        headers: {'Content-Type': 'application/json', 'X-Verification-CSRF': csrf},
        body: JSON.stringify(data)
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        if (payload.retry_after) cooldownUntil = Date.now() + payload.retry_after * 1000;
        throw new Error(payload.message || 'Email confirmation failed. Please try again.');
      }
      return payload;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('The request timed out. Please try again in a minute.');
      if (error instanceof SyntaxError || error instanceof TypeError) throw new Error('Unable to connect. Please try again shortly.');
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }
  email.addEventListener('input', () => {
    revision += 1;
    confirmedEmail = '';
    codeEmail = '';
    challenge.value = '';
    code.value = '';
    fields.hidden = true;
    message('Confirm this email address before sending your inquiry.');
    updateSendButton();
  });
  send.addEventListener('click', async () => {
    if (busy || send.disabled || !email.reportValidity()) return;
    const address = normalizedEmail();
    const attempt = revision;
    busy = true;
    confirmedEmail = '';
    challenge.value = '';
    updateSendButton();
    message('Sending your confirmation code…');
    try {
      const result = await post(panel.dataset.sendUrl, {email: address});
      cooldownUntil = Date.now() + result.retry_after * 1000;
      if (attempt !== revision) return;
      codeEmail = address;
      challenge.value = result.challenge_id;
      fields.hidden = false;
      code.value = '';
      message(result.message + ' The code expires in 10 minutes.');
      code.focus();
    } catch (error) {
      if (attempt === revision) message(error.message, true);
    } finally {
      busy = false;
      updateSendButton();
    }
  });
  confirm.addEventListener('click', async () => {
    if (busy) return;
    if (!/^[0-9]{6}$/.test(code.value.trim())) {
      message('Enter the 6-digit code from your email.', true);
      code.focus();
      return;
    }
    const address = normalizedEmail();
    const attempt = revision;
    if (address !== codeEmail || !challenge.value) {
      message('Request a code for this email address first.', true);
      return;
    }
    busy = true;
    updateSendButton();
    try {
      const result = await post(panel.dataset.confirmUrl, {email: address, challenge_id: challenge.value, code: code.value.trim()});
      if (attempt !== revision) return;
      confirmedEmail = address;
      code.value = '';
      fields.hidden = true;
      message(result.message);
      form.querySelector('[type="submit"]').focus();
    } catch (error) {
      if (attempt === revision) message(error.message, true);
    } finally {
      busy = false;
      updateSendButton();
    }
  });
  code.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); confirm.click(); }
  });
  form.addEventListener('submit', event => {
    if (confirmedEmail && confirmedEmail === normalizedEmail() && challenge.value) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    message('Confirm your email address before sending your inquiry.', true);
    (fields.hidden ? send : code).focus();
  }, true);
  window.addEventListener('pageshow', () => updateSendButton());
  setInterval(updateSendButton, 1000);
  updateSendButton();
})();
