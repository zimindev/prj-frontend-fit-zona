/* Fit Zona — yearly plan: month tabs, progress, exercise technique dialog, print. */
(function () {
  var KEY = 'fz2-plan-' + (document.body.getAttribute('data-plan') || 'x');
  var tabs = [].slice.call(document.querySelectorAll('[role="tab"][data-m]'));
  var panels = [].slice.call(document.querySelectorAll('[data-panel]'));
  var current = 1;

  function load() {
    try { var v = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; }
    catch (e) { return []; }
  }
  function save(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* private mode */ }
  }
  var done = load();

  function renderDone() {
    tabs.forEach(function (t) {
      var m = +t.getAttribute('data-m');
      var isDone = done.indexOf(m) > -1;
      t.classList.toggle('done', isDone);
      t.setAttribute('aria-label', 'Місяць ' + m + (isDone ? ', виконано' : ''));
    });
    document.querySelectorAll('[data-done]').forEach(function (cb) {
      cb.checked = done.indexOf(+cb.getAttribute('data-done')) > -1;
    });
    var n = done.length;
    var txt = document.querySelector('[data-progress-text]');
    var bar = document.querySelector('[data-progress-bar]');
    if (txt) txt.textContent = n + ' з 12 місяців';
    if (bar) bar.style.width = (n / 12 * 100) + '%';
  }

  function show(m, opts) {
    m = Math.min(12, Math.max(1, m | 0));
    current = m;
    tabs.forEach(function (t) {
      var on = +t.getAttribute('data-m') === m;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
    });
    panels.forEach(function (p) { p.hidden = +p.getAttribute('data-panel') !== m; });
    if (opts && opts.hash && location.hash !== '#misyats-' + m) {
      history.replaceState(null, '', '#misyats-' + m);
    }
    if (opts && opts.scroll) {
      document.getElementById('plan').scrollIntoView({ block: 'start' });
    }
  }

  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(+t.getAttribute('data-m'), { hash: true }); });
    t.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (e.key === 'Home') d = -i;
      if (e.key === 'End') d = tabs.length - 1 - i;
      if (!d) return;
      e.preventDefault();
      var next = tabs[(i + d + tabs.length) % tabs.length];
      show(+next.getAttribute('data-m'), { hash: true });
      next.focus();
    });
  });

  // "Month N →" buttons and phase cards
  document.addEventListener('click', function (e) {
    var g = e.target.closest('[data-goto]');
    if (!g) return;
    e.preventDefault();
    show(+g.getAttribute('data-goto'), { hash: true, scroll: true });
  });

  document.addEventListener('change', function (e) {
    var cb = e.target.closest('[data-done]');
    if (!cb) return;
    var m = +cb.getAttribute('data-done');
    done = done.filter(function (x) { return x !== m; });
    if (cb.checked) done.push(m);
    done.sort(function (a, b) { return a - b; });
    save(done);
    renderDone();
  });

  function fromHash() {
    var h = /^#misyats-(\d{1,2})$/.exec(location.hash);
    if (h) { show(+h[1]); return true; }
    return false;
  }
  window.addEventListener('hashchange', fromHash);
  if (!fromHash()) show(1);
  renderDone();

  // print the current month
  var printBtn = document.querySelector('[data-print]');
  if (printBtn) printBtn.addEventListener('click', function () { window.print(); });

  // exercise technique dialog
  var dlg = document.querySelector('.ex-dlg');
  if (dlg && typeof dlg.showModal === 'function') {
    var imgs = dlg.querySelectorAll('.ex-frames img');
    var title = dlg.querySelector('#ex-title');
    var sets = dlg.querySelector('.ex-dlg-sets');
    var opener = null;
    document.addEventListener('click', function (e) {
      var b = e.target.closest('.ex-thumb[data-ex]');
      if (!b) return;
      var id = b.getAttribute('data-ex');
      var name = b.getAttribute('data-name');
      title.textContent = name;
      sets.textContent = b.getAttribute('data-sets');
      imgs[0].src = 'assets/ex/' + id + '-0.webp';
      imgs[1].src = 'assets/ex/' + id + '-1.webp';
      imgs[0].alt = name + ' — початок руху';
      imgs[1].alt = name + ' — кінець руху';
      opener = b;
      dlg.showModal();
    });
    dlg.querySelector('.ex-close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('close', function () { if (opener) opener.focus(); });
  }
})();
