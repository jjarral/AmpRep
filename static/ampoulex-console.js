(() => {
  const menu = document.querySelector('.hamb');
  const nav = document.getElementById('navlinks');
  if (!menu || !nav) return;

  const syncMenuState = (open) => {
    menu.setAttribute('aria-controls', 'navlinks');
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    menu.textContent = open ? '×' : '☰';
  };

  syncMenuState(false);
  menu.addEventListener('click', () => {
    syncMenuState(nav.classList.contains('mobile-menu'));
  });
  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('mobile-menu');
      syncMenuState(false);
    });
  });
})();
