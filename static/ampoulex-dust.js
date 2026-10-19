/* Drifting gold glitter: pseudo-3D depth (size, speed, parallax), flowing curl-like drift, per-particle twinkle over time. Decorative only. */
(function () {
  var cv = document.createElement('canvas'); cv.id = 'dust'; cv.setAttribute('aria-hidden', 'true'); document.body.appendChild(cv);
  var ctx = cv.getContext('2d'); if (!ctx) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches, small = window.innerWidth < 760;
  var dpr = Math.min(window.devicePixelRatio || 1, small ? 1.5 : 2), W = 0, H = 0, mx = 0, my = 0, tmx = 0, tmy = 0, running = false, last = 0, t = 0;
  var COLORS = ['239,207,142', '214,181,115', '255,244,214'], parts = [], sprites = [];
  COLORS.forEach(function (c) {                       /* pre-rendered soft glow sprite per colour */
    var s = document.createElement('canvas'); s.width = s.height = 64; var g = s.getContext('2d'), r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    r.addColorStop(0, 'rgba(' + c + ',1)'); r.addColorStop(.25, 'rgba(' + c + ',.55)'); r.addColorStop(1, 'rgba(' + c + ',0)'); g.fillStyle = r; g.fillRect(0, 0, 64, 64); sprites.push(s);
  });
  function size() { W = window.innerWidth; H = window.innerHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  function seed() {
    var n = small ? 46 : 110; parts = [];
    for (var i = 0; i < n; i++) { var z = Math.pow(Math.random(), 1.6) * .85 + .15;   /* depth: 1 = near, .15 = far */
      parts.push({ x: Math.random() * W, y: Math.random() * H, z: z, s: Math.random() * 6.28, tw: 1.2 + Math.random() * 2.6, c: (Math.random() * 3) | 0, star: Math.random() < .14 && z > .55 }); }
  }
  function frame(now) {
    if (!running) return; var dt = Math.min((now - last) / 1000 || .016, .05); last = now; t += dt;
    mx += (tmx - mx) * .05; my += (tmy - my) * .05;
    var sy = window.scrollY || 0; ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      p.x += Math.sin(p.y * .004 + t * .35 + p.s) * 20 * p.z * dt + Math.cos(p.x * .003 + t * .2) * 8 * p.z * dt;   /* flowing sideways drift */
      p.y -= (9 + 30 * p.z) * dt;                                                                                      /* gentle rise, nearer = faster */
      if (p.y < -20) { p.y = H + 20; p.x = Math.random() * W; } if (p.x < -20) p.x = W + 20; else if (p.x > W + 20) p.x = -20;
      var X = p.x + mx * 46 * p.z, Y = (((p.y - sy * .22 * p.z + my * 30 * p.z) % (H + 40)) + (H + 40)) % (H + 40) - 20;   /* pointer + scroll parallax */
      var tw = .5 + .5 * Math.sin(t * p.tw + p.s), a = (.16 + .62 * p.z) * (.25 + .75 * tw * tw), r = (1.3 + 4.6 * p.z) * (p.z > .85 ? 1.7 : 1);
      ctx.globalAlpha = Math.min(a, .85); ctx.drawImage(sprites[p.c], X - r * 2, Y - r * 2, r * 4, r * 4);
      if (p.star && tw > .82) { var L = r * 5 * tw; ctx.globalAlpha = a * .7; ctx.fillStyle = '#fff4d6'; ctx.fillRect(X - L, Y - .5, L * 2, 1); ctx.fillRect(X - .5, Y - L, 1, L * 2); }   /* glitter flare */
    }
    ctx.globalAlpha = 1;
    if (!reduce && !document.hidden) requestAnimationFrame(frame); else running = false;
  }
  function start() { if (!running) { running = true; last = performance.now(); requestAnimationFrame(frame); } }
  window.addEventListener('pointermove', function (e) { tmx = e.clientX / window.innerWidth - .5; tmy = e.clientY / window.innerHeight - .5; }, { passive: true });
  window.addEventListener('resize', function () { size(); seed(); });
  document.addEventListener('visibilitychange', function () { if (!document.hidden && !reduce) start(); });
  size(); seed(); if (reduce) { running = true; frame(performance.now()); running = false; } else start();
})();
