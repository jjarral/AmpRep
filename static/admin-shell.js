// Shared navigation, account controls, and lightweight live indicators.
const axMenuToggle = document.getElementById('ax-menu-toggle');
const axNavScrim = document.getElementById('ax-nav-scrim');
const axNav = document.getElementById('primary-navigation');
const axNavFilter = document.getElementById('ax-nav-filter');
const axIsMobile = () => window.matchMedia('(max-width: 899.98px)').matches;

function axNavigationIsOpen() {
    return axIsMobile()
        ? document.body.classList.contains('ax-nav-open')
        : !document.body.classList.contains('ax-nav-collapsed');
}

function setNavigationOpen(open, returnFocus = true) {
    const mobile = axIsMobile();
    document.body.classList.toggle('ax-nav-open', mobile && open);
    document.body.classList.toggle('ax-nav-collapsed', !mobile && !open);
    if (axMenuToggle) {
        axMenuToggle.setAttribute('aria-expanded', String(open));
        axMenuToggle.setAttribute('aria-label', open
            ? (mobile ? 'Close navigation menu' : 'Collapse navigation')
            : (mobile ? 'Open navigation menu' : 'Show navigation'));
    }
    if (mobile) {
        if (open && axNavFilter) axNavFilter.focus();
        if (!open && returnFocus && axMenuToggle) axMenuToggle.focus();
    }
}

setNavigationOpen(!axIsMobile(), false);
if (axMenuToggle) axMenuToggle.addEventListener('click', () => setNavigationOpen(!axNavigationIsOpen()));
if (axNavScrim) axNavScrim.addEventListener('click', () => setNavigationOpen(false));
let axWasMobile = axIsMobile();
window.addEventListener('resize', () => {
    const isMobile = axIsMobile();
    if (isMobile !== axWasMobile) setNavigationOpen(!isMobile, false);
    axWasMobile = isMobile;
});

if (axNav) {
    const groups = Array.from(axNav.querySelectorAll('.has-treeview > a.nav-link'));
    groups.forEach((link, index) => {
        const panel = link.parentElement.querySelector(':scope > .nav-treeview');
        if (!panel) return;
        if (!panel.id) panel.id = `ax-nav-group-${index + 1}`;
        link.setAttribute('role', 'button');
        link.setAttribute('aria-controls', panel.id);
        link.setAttribute('aria-expanded', String(link.parentElement.classList.contains('menu-open')));
        link.addEventListener('keydown', event => {
            if (event.key === ' ') {
                event.preventDefault();
                link.click();
            }
        });
    });

    axNav.addEventListener('click', event => {
        const sectionLink = event.target.closest('.has-treeview > a.nav-link');
        if (sectionLink) {
            event.preventDefault();
            const section = sectionLink.parentElement;
            const expanded = section.classList.toggle('menu-open');
            sectionLink.setAttribute('aria-expanded', String(expanded));
            return;
        }
        if (event.target.closest('a.nav-link') && axIsMobile()) setNavigationOpen(false, false);
    });

    const navItems = Array.from(axNav.querySelectorAll('li.nav-item'));
    const navHeaders = Array.from(axNav.querySelectorAll(':scope > ul > li.nav-header'));
    const emptyMessage = document.createElement('p');
    emptyMessage.className = 'ax-nav-empty';
    emptyMessage.textContent = 'No matching sections.';
    emptyMessage.setAttribute('role', 'status');
    axNav.appendChild(emptyMessage);

    function filterNavigation() {
        const query = axNavFilter.value.trim().toLocaleLowerCase();
        navItems.forEach(item => {
            const parentLink = item.querySelector(':scope > a.nav-link');
            const ownText = parentLink ? parentLink.textContent.toLocaleLowerCase() : '';
            const children = Array.from(item.querySelectorAll(':scope > .nav-treeview > .nav-item'));
            if (!children.length) {
                item.hidden = Boolean(query && !ownText.includes(query));
                return;
            }
            const parentMatches = Boolean(query && ownText.includes(query));
            let childMatches = 0;
            children.forEach(child => {
                const matches = !query || parentMatches || child.textContent.toLocaleLowerCase().includes(query);
                child.hidden = !matches;
                if (matches) childMatches += 1;
            });
            item.hidden = Boolean(query && !parentMatches && !childMatches);
            if (query && childMatches && !parentMatches) {
                item.classList.add('menu-open');
                if (parentLink) parentLink.setAttribute('aria-expanded', 'true');
            } else if (!query) {
                const expanded = Boolean(item.querySelector('.nav-link.active'));
                item.classList.toggle('menu-open', expanded);
                if (parentLink) parentLink.setAttribute('aria-expanded', String(expanded));
            }
        });

        navHeaders.forEach(header => {
            let sibling = header.nextElementSibling;
            let hasVisibleItem = false;
            while (sibling && !sibling.classList.contains('nav-header')) {
                if (sibling.classList.contains('nav-item') && !sibling.hidden) hasVisibleItem = true;
                sibling = sibling.nextElementSibling;
            }
            header.hidden = Boolean(query && !hasVisibleItem);
        });
        emptyMessage.style.display = query && !navItems.some(item => !item.hidden) ? 'block' : 'none';
    }

    navItems.forEach(item => {
        const activeLink = item.querySelector(':scope > a.nav-link.active');
        if (activeLink && activeLink.getAttribute('href') !== '#') activeLink.setAttribute('aria-current', 'page');
    });
    if (axNavFilter) axNavFilter.addEventListener('input', filterNavigation);
}

document.addEventListener('keydown', event => {
    const target = event.target;
    const isTyping = target instanceof HTMLElement
        && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName));
    if (event.key === 'Escape' && document.body.classList.contains('ax-nav-open')) setNavigationOpen(false);
    if (event.key === '/' && !isTyping && !event.altKey && !event.ctrlKey && !event.metaKey && axNavFilter) {
        event.preventDefault();
        axNavFilter.focus();
    }
});

// Native account menu keeps working when optional framework scripts are unavailable.
const axAccountToggle = document.getElementById('ax-account-toggle');
const axAccountMenu = document.getElementById('ax-account-menu');
function setAccountMenuOpen(open) {
    if (!axAccountToggle || !axAccountMenu) return;
    axAccountMenu.hidden = !open;
    axAccountToggle.setAttribute('aria-expanded', String(open));
}
if (axAccountToggle && axAccountMenu) {
    setAccountMenuOpen(false);
    axAccountToggle.addEventListener('click', () => setAccountMenuOpen(axAccountMenu.hidden));
    document.addEventListener('click', event => {
        if (!event.target.closest('.main-header .dropdown')) setAccountMenuOpen(false);
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !axAccountMenu.hidden) {
            setAccountMenuOpen(false);
            axAccountToggle.focus();
        }
    });
}

document.addEventListener('click', event => {
    const dismiss = event.target.closest('[data-dismiss="alert"]');
    if (dismiss) dismiss.closest('.alert')?.remove();
});

const axClock = document.getElementById('ax-header-clock');
if (axClock) {
    const updateClock = () => { axClock.textContent = new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date()); };
    updateClock();
    window.setInterval(updateClock, 30_000);
}

if (typeof window.io === 'function' && typeof window.socket === 'undefined') {
    window.socket = window.io('/admin', { reconnection: true, reconnectionAttempts: 5 });
    window.socket.on('new_inquiry', data => showToast('New inquiry', `${data.customer} · ${data.business}`, 'info'));
    window.socket.on('new_order', data => showToast('New order', `${data.customer} · PKR ${data.total}`, 'success'));
}

function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top:88px;right:20px;z-index:1090;width:min(390px,calc(100vw - 32px));box-shadow:0 14px 34px rgba(0,0,0,.28);';
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    const heading = document.createElement('strong');
    heading.textContent = title;
    const detail = document.createElement('div');
    detail.textContent = message;
    detail.style.marginTop = '4px';
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'close';
    close.setAttribute('aria-label', 'Dismiss notification');
    close.textContent = '×';
    close.addEventListener('click', () => toast.remove());
    toast.append(heading, detail, close);
    document.body.appendChild(toast);
    window.setTimeout(() => toast.remove(), 5000);
}

function updateInquiryBadge() {
    fetch('/api/inquiry-count', { headers: { Accept: 'application/json' } })
        .then(response => response.ok ? response.json() : null)
        .then(data => {
            const badge = document.getElementById('inquiry-badge');
            if (!badge || !data) return;
            const count = Number(data.count) || 0;
            badge.textContent = count;
            badge.hidden = count < 1;
            badge.setAttribute('aria-label', `${count} open inquiries`);
        })
        .catch(() => {});
}
document.addEventListener('DOMContentLoaded', () => {
    updateInquiryBadge();
    window.setInterval(updateInquiryBadge, 45_000);
});
