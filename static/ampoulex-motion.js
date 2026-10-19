/* Ampoulex motion system: curtain intro, SplitText mask reveals, scroll-velocity marquee, cursor ring, tilt cards, progress line,
   Lenis smooth scroll, Motion spring buttons. Everything is skipped for reduced-motion users. */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var G = window.gsap, ST = window.ScrollTrigger, SP = window.SplitText, M = window.Motion, lenis = null, fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (!G) return; G.registerPlugin.apply(G, [ST, SP].filter(Boolean));

  /* Lenis smooth scroll, driven by the GSAP ticker */
  if (window.Lenis) {
    lenis = new Lenis({ lerp: .1, smoothWheel: true });
    if (ST) lenis.on('scroll', ST.update); G.ticker.add(function (t) { lenis.raf(t * 1000); }); G.ticker.lagSmoothing(0);
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) { var id = a.getAttribute('href'), el = id.length > 1 && document.querySelector(id); if (el) { e.preventDefault(); lenis.scrollTo(el, { offset: -84 }); } });
    });
  }

  /* Curtain intro (first visit per session) */
  var first = true, delay = .05; try { first = !sessionStorage.getItem('ax-intro'); sessionStorage.setItem('ax-intro', '1'); } catch (e) {}
  if (first) {
    var logo = document.querySelector('.brand img'), ov = document.createElement('div'); ov.id = 'intro'; ov.setAttribute('aria-hidden', 'true');
    ov.innerHTML = (logo ? '<img src="' + logo.src + '" alt="">' : '') + '<i></i>'; document.body.appendChild(ov); delay = 1.15;
    var tl = G.timeline({ onComplete: function () { ov.remove(); } });
    tl.from(ov.querySelector('img') || ov, { autoAlpha: 0, scale: .9, duration: .55, ease: 'power2.out' }).from(ov.querySelector('i'), { scaleX: 0, duration: .6, ease: 'power3.inOut' }, '-=.2').to(ov, { yPercent: -100, duration: .85, ease: 'expo.inOut' }, '+=.1');
    setTimeout(function () { if (ov.parentNode) ov.remove(); }, 4000);
  }

  function boot() {
    /* hero: masked line reveal, then supporting copy */
    var h1 = document.querySelector('.hero-copy h1');
    if (h1 && SP) SP.create(h1, { type: 'lines', mask: 'lines', maskClass: 'sp-mask', autoSplit: true, onSplit: function (s) { return G.from(s.lines, { yPercent: 118, duration: 1.3, stagger: .13, ease: 'expo.out', delay: delay }); } });
    G.from('.hero-description, .hero-actions', { y: 26, autoAlpha: 0, duration: 1, stagger: .14, ease: 'power3.out', delay: delay + .55, clearProps: 'all' });
    G.from('.hero-visual', { autoAlpha: 0, scale: .96, duration: 1.4, ease: 'power3.out', delay: delay + .2, clearProps: 'opacity,visibility,scale' });

    /* section headings */
    document.querySelectorAll('section h2').forEach(function (h) {
      if (SP) SP.create(h, { type: 'lines', mask: 'lines', maskClass: 'sp-mask', autoSplit: true, onSplit: function (s) { return G.from(s.lines, { yPercent: 112, duration: 1.15, stagger: .1, ease: 'expo.out', scrollTrigger: { trigger: h, start: 'top 88%', once: true } }); } });
    });

    /* product cards: staggered entrance */
    var cards = document.querySelectorAll('.product-card');
    if (cards.length && ST) { G.set(cards, { autoAlpha: 0, y: 40 }); ST.batch(cards, { start: 'top 94%', once: true, onEnter: function (b) { G.to(b, { autoAlpha: 1, y: 0, stagger: .07, duration: .9, ease: 'power3.out', clearProps: 'all', overwrite: true }); } }); }

    /* section 3: technical drawing draws itself, then the dimension lines fade in */
    var ol = document.querySelector('.spec-outline');
    if (ol && ST) {
      var len = ol.getTotalLength(), dm = document.querySelectorAll('.spec-drawing .dim');
      G.set(ol, { strokeDasharray: len, strokeDashoffset: len }); G.set(dm, { autoAlpha: 0 });
      G.timeline({ scrollTrigger: { trigger: '.spec-figure', start: 'top 80%', once: true } }).to(ol, { strokeDashoffset: 0, duration: 1.8, ease: 'power2.inOut' }).to(dm, { autoAlpha: 1, duration: .6, stagger: .08, clearProps: 'opacity,visibility' }, '-=.5');
    }

    /* hero parallax + progress line */
    var hv = document.querySelector('.hero-visual');
    if (hv && ST) G.to(hv, { yPercent: -5, ease: 'none', scrollTrigger: { trigger: hv, start: 'top bottom', end: 'bottom top', scrub: true } });
    var bar = document.createElement('div'); bar.id = 'progress'; bar.setAttribute('aria-hidden', 'true'); document.body.appendChild(bar);
    if (ST) G.to(bar, { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: .3 } });

    /* marquee between hero and range; speed follows scroll velocity */
    var anchor = document.getElementById('products');
    if (anchor) {
      var words = ['Clear glass', 'Amber glass', '1 mL', '2 mL', '3 mL', '5 mL', '10 mL', 'Ampoule painting', 'Wah Cantt, Pakistan'], set = words.map(function (w) { return '<span>' + w + '</span>'; }).join('');
      var mq = document.createElement('div'); mq.className = 'marquee'; mq.setAttribute('aria-hidden', 'true'); mq.innerHTML = '<div class="marquee-track">' + set + set + set + set + '</div>';
      anchor.parentNode.insertBefore(mq, anchor);
      var tr = mq.firstChild, tween = G.to(tr, { xPercent: -50, duration: 38, ease: 'none', repeat: -1 });
      if (lenis) lenis.on('scroll', function (e) { G.to(tween, { timeScale: 1 + Math.min(Math.abs(e.velocity) * .35, 7), duration: .25, overwrite: true }).then(function () { G.to(tween, { timeScale: 1, duration: 1.2 }); }); });
    }

    /* desktop: cursor ring + tilting cards with light glare */
    if (fine) {
      var ring = document.createElement('div'); ring.id = 'cursor'; ring.setAttribute('aria-hidden', 'true'); document.body.appendChild(ring);
      var qx = G.quickTo(ring, 'x', { duration: .4, ease: 'power3' }), qy = G.quickTo(ring, 'y', { duration: .4, ease: 'power3' });
      window.addEventListener('pointermove', function (e) { qx(e.clientX); qy(e.clientY); ring.classList.add('on'); }, { passive: true });
      document.addEventListener('pointerleave', function () { ring.classList.remove('on'); });
      document.addEventListener('pointerover', function (e) { ring.classList.toggle('hot', !!e.target.closest('a, button, label, summary, .product-card')); });
      cards.forEach(function (c) {
        c.addEventListener('pointermove', function (e) { var b = c.getBoundingClientRect(), x = (e.clientX - b.left) / b.width, y = (e.clientY - b.top) / b.height; c.style.setProperty('--ry', ((x - .5) * 9).toFixed(2) + 'deg'); c.style.setProperty('--rx', ((.5 - y) * 7).toFixed(2) + 'deg'); c.style.setProperty('--gx', (x * 100) + '%'); c.style.setProperty('--gy', (y * 100) + '%'); });
        c.addEventListener('pointerleave', function () { c.style.setProperty('--ry', '0deg'); c.style.setProperty('--rx', '0deg'); });
      });
    }
    if (ST) window.addEventListener('load', function () { ST.refresh(); });
  }
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(boot);

  /* Motion (Framer Motion's vanilla engine): spring hover and press on buttons */
  if (M && M.hover && fine) {
    var spring = { type: 'spring', stiffness: 320, damping: 22 };
    M.hover('.button, .button-small', function (el) { M.animate(el, { y: -2, scale: 1.025 }, spring); return function () { M.animate(el, { y: 0, scale: 1 }, spring); }; });
    M.press('.button, .button-small', function (el) { M.animate(el, { scale: .96 }, spring); return function () { M.animate(el, { scale: 1 }, spring); }; });
  }
})();
