/* Fit Zona — меню і шапка. */
(function () {
  var burger = document.querySelector('.burger');
  var nav = document.getElementById('site-nav');
  var header = document.querySelector('.site-header');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') !== 'true';
      burger.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('open', open);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        burger.setAttribute('aria-expanded', 'false');
        nav.classList.remove('open');
        burger.focus();
      }
    });
  }
  if (header) {
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();
