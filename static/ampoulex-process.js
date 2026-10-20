/* Ampoulex — scroll-driven 3D "tube to ampoule" story. Shape = the site's ampoule silhouette (ampoulex-profile.json). */
(function () {
  var sec = document.getElementById('process');
  if (!sec) return;
  var canvas = document.getElementById('process-canvas');
  var steps = [].slice.call(sec.querySelectorAll('.process-step'));
  var nameEl = document.getElementById('process-stage-name');
  var barEl = document.getElementById('process-bar');
  var NAMES = ['GLASS TUBE', 'HEATING', 'FORMING', 'ANNEALING', 'FINISHED'];
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var webgl = (function () { try { var c = document.createElement('canvas'); return !!(window.WebGLRenderingContext && (c.getContext('webgl') || c.getContext('experimental-webgl'))); } catch (e) { return false; } })();
  if (reduce || !webgl) return; // static chapter list remains

  function load(src, cb) { var s = document.createElement('script'); s.src = src; s.onload = cb; s.onerror = function () {}; document.head.appendChild(s); }
  function getProfile(cb) {
    if (window.AX_PROFILE) return cb(window.AX_PROFILE);
    fetch(sec.dataset.profile).then(function (r) { return r.json(); }).then(cb).catch(function () {});
  }
  var started = false;
  function boot() {
    if (started) return; started = true;
    getProfile(function (prof) {
      var go = function () { try { init(prof); } catch (e) { sec.classList.remove('is-live'); console.warn('process 3D off', e); } };
      if (window.THREE) go(); else load(sec.dataset.three, go);
    });
  }
  var io = new IntersectionObserver(function (e) { if (e[0].isIntersecting) { boot(); io.disconnect(); } }, { rootMargin: '600px 0px' });
  io.observe(sec);

  function init(prof) {
    var THREE = window.THREE, N = prof.length, SEG = 72;
    sec.classList.add('is-live');
    var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    var scene = new THREE.Scene();
    var cam = new THREE.PerspectiveCamera(28, 1, 0.1, 100);

    // environment: soft studio panels baked via PMREM
    var envScene = new THREE.Scene();
    var box = new THREE.Mesh(new THREE.BoxGeometry(20, 20, 20), new THREE.MeshBasicMaterial({ color: 0x050505, side: THREE.BackSide }));
    envScene.add(box);
    function panel(w, h, x, y, z, c, i) {
      var m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(c).multiplyScalar(i), side: THREE.DoubleSide }));
      m.position.set(x, y, z); m.lookAt(0, 0, 0); envScene.add(m);
    }
    panel(8, 14, -8, 2, 4, 0xffffff, 3); panel(3, 14, 8, 0, 3, 0xefcf8e, 4); panel(14, 3, 0, 9, 0, 0xffffff, 2.5); panel(10, 4, 0, -8, 4, 0xd6b573, 1.2);
    var pm = new THREE.PMREMGenerator(renderer);
    var env = pm.fromScene(envScene, 0.02).texture; scene.environment = env;

    // geometry helpers: lathe over (profile index i) x (segment j)
    var count = N * (SEG + 1);
    var pos = new Float32Array(count * 3), col = new Float32Array(count * 3);
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    var idx = [];
    for (var i = 0; i < N - 1; i++) for (var j = 0; j < SEG; j++) {
      var a = i * (SEG + 1) + j, b = a + 1, c = a + SEG + 1, d = c + 1;
      idx.push(a, c, b, b, c, d);
    }
    geo.setIndex(idx);
    var TUBE_R = 0.5, H = prof[N - 1][1];

    var glass = new THREE.MeshPhysicalMaterial({ color: 0xd8ecf2, metalness: 0, roughness: 0.04, transparent: true, opacity: 0.34, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.7, side: THREE.DoubleSide, depthWrite: false });
    var body = new THREE.Mesh(geo, glass);
    var heatMat = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
    var heat = new THREE.Mesh(geo, heatMat);
    var g = new THREE.Group(); g.add(body); g.add(heat); g.position.y = -H / 2; var pivot = new THREE.Group(); pivot.add(g); scene.add(pivot);

    // gold finish band (subset of profile, slightly proud of the glass)
    var y0 = 0.45, y1 = 2.35, bi = [];
    prof.forEach(function (p, k) { if (p[1] >= y0 && p[1] <= y1 && p[0] > 0.3) bi.push(k); });
    var lo = bi[0], hi = bi[bi.length - 1], bn = hi - lo + 1;
    var bpos = new Float32Array(bn * (SEG + 1) * 3);
    for (var q = 0; q < bn; q++) for (var s = 0; s <= SEG; s++) {
      var an = s / SEG * Math.PI * 2, r = prof[lo + q][0] * 1.012, o = (q * (SEG + 1) + s) * 3;
      bpos[o] = Math.cos(an) * r; bpos[o + 1] = prof[lo + q][1]; bpos[o + 2] = Math.sin(an) * r;
    }
    var bg = new THREE.BufferGeometry(); bg.setAttribute('position', new THREE.BufferAttribute(bpos, 3));
    var bidx = []; for (var u = 0; u < bn - 1; u++) for (var v = 0; v < SEG; v++) { var A = u * (SEG + 1) + v, B = A + 1, C = A + SEG + 1, D = C + 1; bidx.push(A, C, B, B, C, D); }
    bg.setIndex(bidx); bg.computeVertexNormals();
    var gold = new THREE.MeshPhysicalMaterial({ color: 0xd6b573, metalness: 1, roughness: 0.22, envMapIntensity: 1.6, transparent: true, opacity: 0, side: THREE.DoubleSide });
    var band = new THREE.Mesh(bg, gold); band.visible = false; g.add(band);

    // rim glint ring at the open tip
    var rimR = prof[N - 1][0];
    var rim = new THREE.Mesh(new THREE.TorusGeometry(rimR, 0.012, 8, 72), new THREE.MeshBasicMaterial({ color: 0xefcf8e, transparent: true, opacity: 0 }));
    rim.rotation.x = Math.PI / 2; rim.position.y = H; g.add(rim);

    var key = new THREE.PointLight(0xefcf8e, 20, 30); key.position.set(4, 3, 6); scene.add(key);
    var fill = new THREE.PointLight(0x9fd0ff, 8, 30); fill.position.set(-5, -1, 4); scene.add(fill);
    var hot = new THREE.PointLight(0xff7a22, 0, 14); hot.position.set(0, 0, 3); scene.add(hot);

    function sm(a, b, x) { x = Math.min(1, Math.max(0, (x - a) / (b - a))); return x * x * (3 - 2 * x); }
    var cur = { morph: -1, heat: -1 };
    function build(morph, hv, t) {
      for (var i = 0; i < N; i++) {
        var u = i / (N - 1);
        var m = sm(0, 1, Math.min(1, Math.max(0, morph * 1.6 - u * 0.6)));
        var r = TUBE_R + (prof[i][0] - TUBE_R) * m, y = prof[i][1];
        // heat is strongest mid-body, travels up as the tube is worked
        var w = Math.exp(-Math.pow((u - (0.2 + 0.6 * morph)) * 3.2, 2)) * hv + hv * 0.35;
        var hc = Math.min(1, w);
        for (var j = 0; j <= SEG; j++) {
          var an = j / SEG * Math.PI * 2, o = (i * (SEG + 1) + j) * 3;
          pos[o] = Math.cos(an) * r; pos[o + 1] = y; pos[o + 2] = Math.sin(an) * r;
          col[o] = hc * 1.0; col[o + 1] = hc * (0.28 + 0.2 * hc); col[o + 2] = hc * 0.04;
        }
      }
      geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true; geo.computeVertexNormals();
    }

    function size() {
      var w = canvas.clientWidth || 600, h = canvas.clientHeight || 600;
      renderer.setSize(w, h, false); cam.aspect = w / h;
      cam.position.set(0, 0.2, w / h < 0.9 ? 15.5 : 12.5); cam.lookAt(0, 0, 0); cam.updateProjectionMatrix();
    }
    size(); addEventListener('resize', size);

    var target = 0, prog = 0, visible = true, last = 0, stage = -1;
    function readP() {
      var r = sec.getBoundingClientRect(), span = Math.max(1, r.height - innerHeight);
      target = Math.min(1, Math.max(0, -r.top / span));
    }
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) loop(performance.now()); }, { rootMargin: '100px' }).observe(sec);
    addEventListener('scroll', readP, { passive: true }); readP();
    size();

    function loop(now) {
      if (!visible) return;
      requestAnimationFrame(loop);
      var dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
      prog += (target - prog) * (1 - Math.pow(0.001, dt));
      var p = prog;
      var morph = sm(0.38, 0.66, p);
      var hv = sm(0.16, 0.34, p) * (1 - sm(0.64, 0.84, p));
      var flicker = 1 + Math.sin(now * 0.011) * 0.04;
      var mk = Math.round(morph * 400), hk = Math.round(hv * 400);
      if (mk !== cur.morph || hk !== cur.heat) { build(mk / 400, hv * flicker, now); cur.morph = mk; cur.heat = hk; }
      hot.intensity = hv * 40; heatMat.opacity = 0.9;
      glass.opacity = 0.34 - hv * 0.12;
      var pa = sm(0.82, 0.95, p);
      band.visible = pa > 0.01; gold.opacity = pa; rim.material.opacity = sm(0.7, 0.85, p) * 0.9;
      pivot.rotation.y = p * Math.PI * 3.2 + now * 0.00012;
      pivot.rotation.z = Math.sin(p * 3.1) * 0.05; pivot.rotation.x = 0.1 - p * 0.05;
      pivot.position.y = Math.sin(now * 0.0009) * 0.05;
      var sc = 1 + sm(0.85, 1, p) * 0.08; pivot.scale.set(sc, sc, sc);
      renderer.render(scene, cam);

      var st = p < 0.16 ? 0 : p < 0.38 ? 1 : p < 0.66 ? 2 : p < 0.82 ? 3 : 4;
      if (st !== stage) {
        stage = st; if (nameEl) nameEl.textContent = NAMES[st];
        steps.forEach(function (el, k) { el.classList.toggle('is-on', k === st); el.classList.toggle('is-past', k < st); });
      }
      if (barEl) barEl.style.transform = 'scaleX(' + p.toFixed(3) + ')';
    }
    build(0, 0, 0); cur.morph = 0; cur.heat = 0;
    loop(performance.now());
    window.__axProcess = { set: function (v) { target = prog = v; }, get p() { return prog; } };
  }
})();
