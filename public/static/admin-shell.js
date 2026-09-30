
// Responsive navigation and quick section filter.
const axMenuToggle = document.getElementById('ax-menu-toggle');
const axNavScrim = document.getElementById('ax-nav-scrim');
const axNav = document.getElementById('primary-navigation');
const axNavFilter = document.getElementById('ax-nav-filter');
function setNavigationOpen(open, returnFocus = true) {
    document.body.classList.toggle('ax-nav-open', open);
    if (axMenuToggle) {
        axMenuToggle.setAttribute('aria-expanded', String(open));
        axMenuToggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    }
    if (window.matchMedia('(max-width: 767.98px)').matches) {
        if (open && axNavFilter) axNavFilter.focus();
        if (!open && returnFocus && axMenuToggle) axMenuToggle.focus();
    }
}
if (axMenuToggle) axMenuToggle.addEventListener('click', () => setNavigationOpen(!document.body.classList.contains('ax-nav-open')));
if (axNavScrim) axNavScrim.addEventListener('click', () => setNavigationOpen(false));
document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.body.classList.contains('ax-nav-open')) setNavigationOpen(false);
});
if (axNav) {
    axNav.querySelectorAll('.has-treeview > a.nav-link').forEach(link => {
        link.setAttribute('aria-expanded', String(link.parentElement.classList.contains('menu-open')));
    });
    axNav.addEventListener('click', event => {
        const sectionLink = event.target.closest('.has-treeview > a.nav-link');
        if (sectionLink) {
            event.preventDefault();
            event.stopPropagation();
            const section = sectionLink.parentElement;
            const expanded = section.classList.toggle('menu-open');
            sectionLink.setAttribute('aria-expanded', String(expanded));
            return;
        }
        if (event.target.closest('a.nav-link') && window.matchMedia('(max-width: 767.98px)').matches) setNavigationOpen(false, false);
    });
}

// Native account menu, independent of the optional Bootstrap JavaScript.
const axAccountToggle = document.getElementById('ax-account-toggle');
const axAccountMenu = document.getElementById('ax-account-menu');
function setAccountMenuOpen(open) {
    if (!axAccountToggle || !axAccountMenu) return;
    axAccountMenu.hidden = !open;
    axAccountToggle.setAttribute('aria-expanded', String(open));
}
if (axAccountToggle && axAccountMenu) {
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
    if (dismiss) {
        const alert = dismiss.closest('.alert');
        if (alert) alert.remove();
    }
});

if (axNavFilter && axNav) {
    const navItems = Array.from(axNav.querySelectorAll('li.nav-item'));
    const navHeaders = Array.from(axNav.querySelectorAll(':scope > ul > li.nav-header'));
    const emptyMessage = document.createElement('p');
    emptyMessage.className = 'ax-nav-empty';
    emptyMessage.textContent = 'No matching sections.';
    emptyMessage.setAttribute('aria-live', 'polite');
    axNav.appendChild(emptyMessage);

    function filterNavigation() {
        const query = axNavFilter.value.trim().toLocaleLowerCase();
        navItems.forEach(item => {
            const parentLink = item.querySelector(':scope > a.nav-link');
            const ownText = parentLink ? parentLink.textContent.toLocaleLowerCase() : '';
            const children = Array.from(item.querySelectorAll('.nav-treeview > .nav-item'));
            if (!children.length) {
                item.hidden = Boolean(query && !ownText.includes(query));
                return;
            }
            const parentMatches = Boolean(query && ownText.includes(query));
            let childMatches = 0;
            children.forEach(child => {
                const text = child.textContent.toLocaleLowerCase();
                const matches = !query || parentMatches || text.includes(query);
                child.hidden = !matches;
                if (matches) childMatches += 1;
            });
            item.hidden = Boolean(query && !parentMatches && !childMatches);
            const sectionLink = item.querySelector(':scope > a.nav-link');
            if (query && childMatches && !parentMatches) {
                item.classList.add('menu-open');
                if (sectionLink) sectionLink.setAttribute('aria-expanded', 'true');
            } else if (!query) {
                const expanded = Boolean(item.querySelector('.nav-link.active'));
                item.classList.toggle('menu-open', expanded);
                if (sectionLink) sectionLink.setAttribute('aria-expanded', String(expanded));
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
    axNavFilter.addEventListener('input', filterNavigation);
}

// Socket.IO - single connection guard
if (typeof window.io === 'function' && typeof window.socket === 'undefined') {
    window.socket = io('/admin', { reconnection: true, reconnectionAttempts: 5 });
    window.socket.on('connect', () => console.log('✅ Real-time connected'));
    window.socket.on('new_inquiry', d => showToast('New inquiry', `${d.customer} · ${d.business}`, 'info'));
    window.socket.on('new_order', d => showToast('New order', `${d.customer} · PKR ${d.total}`, 'success'));
}
function showToast(title, msg, type='info') {
    const t = document.createElement('div');
    t.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    t.style.cssText = 'top:82px; right:20px; z-index:1090; width:min(380px,calc(100vw - 32px)); box-shadow:0 12px 34px rgba(17,25,29,.16);';
    t.setAttribute('role', 'status');
    t.setAttribute('aria-live', 'polite');
    const heading = document.createElement('strong');
    heading.textContent = title;
    const detail = document.createElement('div');
    detail.textContent = msg;
    detail.style.marginTop = '4px';
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'close';
    close.setAttribute('aria-label', 'Dismiss notification');
    close.textContent = '×';
    close.addEventListener('click', () => t.remove());
    t.append(heading, detail, close);
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 5000);
}
// Badge updates
function updateInquiryBadge() {
    fetch('/api/inquiry-count', { headers: { 'Accept': 'application/json' } })
        .then(r => r.json())
        .then(d => {
            const el = document.getElementById('inquiry-badge');
            if (el) {
                el.textContent = d.count;
                el.style.display = d.count > 0 ? 'inline' : 'none';
                el.setAttribute('aria-label', `${d.count} open inquiries`);
            }
        })
        .catch(() => {});
}
document.addEventListener('DOMContentLoaded', () => { updateInquiryBadge(); setInterval(updateInquiryBadge, 30000); });
