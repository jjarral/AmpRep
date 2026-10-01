(() => {
  'use strict';
  const menu = document.getElementById('menu-toggle');
  const nav = document.getElementById('main-nav');
  function closeMenu() {
    nav.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation');
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    nav.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) { closeMenu(); menu.focus(); }
  });

  const checks = Array.from(document.querySelectorAll('.product-check'));
  const addButtons = Array.from(document.querySelectorAll('[data-add-product]'));
  const dock = document.getElementById('inquiry-dock');
  const feedback = document.getElementById('selector-feedback');
  const toast = document.getElementById('selection-toast');
  let toastTimer;
  let contactInView = false;
  function syncSelection() {
    const selected = checks.filter(check => check.checked);
    let total = 0;
    let missing = false;
    checks.forEach(check => {
      const quantity = document.getElementById(check.dataset.quantity);
      quantity.disabled = !check.checked;
      quantity.required = check.checked;
      check.closest('.product-option').classList.toggle('selected', check.checked);
      if (check.checked) {
        const value = Number(quantity.value);
        if (Number.isInteger(value) && value > 0) total += value;
        else missing = true;
      }
    });
    addButtons.forEach(button => {
      const selected = document.getElementById(`product-${button.dataset.addProduct}`)?.checked;
      button.classList.toggle('is-added', !!selected);
      button.querySelector('span').textContent = selected ? 'Added to inquiry' : 'Add to inquiry';
      button.querySelector('b').textContent = selected ? '✓' : '+';
    });
    const count = selected.length;
    const noun = count === 1 ? 'format' : 'formats';
    document.getElementById('selection-total').textContent = count
      ? `${count} ${noun} selected${total ? ` · ${total.toLocaleString()} pieces` : ''}${missing ? ' · Enter quantities to continue.' : ''}`
      : 'Select your ampoule formats above.';
    document.getElementById('dock-count').textContent = count;
    document.getElementById('dock-label').textContent = `ampoule ${noun} selected`;
    dock.hidden = !count || contactInView;
  }
  function addProduct(check) {
    if (!check) return false;
    const alreadySelected = check.checked;
    check.checked = true;
    syncSelection();
    toast.textContent = `${check.dataset.name} ${alreadySelected ? 'is already in' : 'added to'} your inquiry.`;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 4500);
    return true;
  }
  checks.forEach(check => {
    check.addEventListener('change', syncSelection);
    document.getElementById(check.dataset.quantity).addEventListener('input', syncSelection);
  });
  addButtons.forEach(button => button.addEventListener('click', () => addProduct(document.getElementById(`product-${button.dataset.addProduct}`))));
  const selector = document.getElementById('quick-selector');
  if (selector) {
    selector.hidden = false;
    const quickButton = document.getElementById('add-selection');
    function currentProduct() {
      const volume = document.querySelector('[name="quick-size"]:checked').value;
      const color = document.querySelector('[name="quick-color"]:checked').value;
      return checks.find(check => check.dataset.volume === volume && check.dataset.color === color);
    }
    function syncQuickSelector() {
      const product = currentProduct();
      quickButton.disabled = !product;
      feedback.textContent = product ? `${product.dataset.name} · Select a quantity in your inquiry.` : 'This format is not currently listed. Contact us for details.';
    }
    selector.querySelectorAll('input').forEach(input => input.addEventListener('change', syncQuickSelector));
    quickButton.addEventListener('click', () => {
      const product = currentProduct();
      if (addProduct(product)) feedback.textContent = `${product.dataset.name} added. Choose another format or review your inquiry.`;
    });
    syncQuickSelector();
  }
  const filters = document.querySelector('.filter-controls');
  if (filters) {
    filters.hidden = false;
    filters.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      filters.querySelectorAll('button').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      document.querySelectorAll('.product-card').forEach(card => {
        card.hidden = button.dataset.filter !== 'all' && card.dataset.color !== button.dataset.filter;
      });
    }));
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { contactInView = entries[0].isIntersecting; syncSelection(); },
      {threshold: 0, rootMargin: '0px 0px -15% 0px'}).observe(document.getElementById('contact'));
  }
  const form = document.getElementById('quote-form');
  const serviceRadios = Array.from(form.querySelectorAll('[name="service_type"]'));
  const optionalSpecifications = document.getElementById('optional-specifications');
  function syncServiceChoice() {
    const service = serviceRadios.find(radio => radio.checked)?.value;
    const needsPainting = service === 'painting' || service === 'supply_and_painting';
    optionalSpecifications.classList.toggle('painting-request', needsPainting);
    if (needsPainting) optionalSpecifications.open = true;
  }
  serviceRadios.forEach(radio => radio.addEventListener('change', syncServiceChoice));
  document.querySelectorAll('[data-enquiry-service="painting"]').forEach(link => link.addEventListener('click', () => {
    const paintingRadio = serviceRadios.find(radio => radio.value === 'painting');
    if (paintingRadio) {
      paintingRadio.checked = true;
      paintingRadio.dispatchEvent(new Event('change', { bubbles: true }));
      syncServiceChoice();
    }
  }));
  syncServiceChoice();
  const inquiryAdd = document.getElementById('inquiry-add');
  const productPicker = document.getElementById('inquiry-product-picker');
  if (inquiryAdd && productPicker) {
    inquiryAdd.hidden = false;
    form.classList.add('is-enhanced');
    document.getElementById('inquiry-add-button').addEventListener('click', () => {
      const check = document.getElementById(`product-${productPicker.value}`);
      if (addProduct(check)) document.getElementById(check.dataset.quantity).focus();
    });
    checks.forEach(check => check.addEventListener('change', () => {
      if (!check.checked) productPicker.focus();
    }));
  }
  form.addEventListener('submit', event => {
    const error = document.getElementById('form-error');
    if (!checks.some(check => check.checked)) {
      event.preventDefault();
      error.textContent = 'Please select at least one ampoule format and enter its quantity.';
      error.hidden = false;
      (productPicker || checks[0])?.focus();
      return;
    }
    const invalidQuantity = checks.some(check => {
      if (!check.checked) return false;
      const quantity = Number(document.getElementById(check.dataset.quantity).value);
      return !Number.isInteger(quantity) || quantity < 1;
    });
    if (invalidQuantity) {
      event.preventDefault();
      error.textContent = 'Enter a whole-number quantity of at least 1 for each selected format.';
      error.hidden = false;
      const firstInvalid = checks.find(check => check.checked && (!Number.isInteger(Number(document.getElementById(check.dataset.quantity).value)) || Number(document.getElementById(check.dataset.quantity).value) < 1));
      if (firstInvalid) document.getElementById(firstInvalid.dataset.quantity).focus();
      return;
    }
    error.hidden = true;
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true;
    submit.firstChild.textContent = 'Sending inquiry… ';
  });
  window.addEventListener('pageshow', () => {
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = false;
    submit.firstChild.textContent = 'Send inquiry ';
    syncSelection();
  });
  syncSelection();
  if (document.querySelector('.form-flash')) {
    document.getElementById('contact').scrollIntoView({behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  }
})();
