/* Song ngữ VI / EN cho toàn site: mọi phần tử có data-vi + data-en, nút [data-lang], nhớ lựa chọn khi chuyển trang. */
(function () {
  var KEY = 'vrcLang', d = document, root = d.documentElement;
  function saved() {
    var q = (location.search.match(/[?&]lang=(vi|en)\b/) || [])[1];
    if (q) return q;
    try { return localStorage.getItem(KEY) === 'en' ? 'en' : 'vi'; } catch (e) { return 'vi'; }
  }
  function apply(lang) {
    root.setAttribute('lang', lang);
    root.setAttribute('data-lang', lang);
    var nodes = d.querySelectorAll('[data-vi][data-en]');
    for (var i = 0; i < nodes.length; i++) {
      var v = nodes[i].getAttribute('data-' + lang);
      if (v !== null && v !== '' && nodes[i].innerHTML !== v) nodes[i].innerHTML = v;
    }
    var alts = d.querySelectorAll('[data-alt-en]');
    for (var k = 0; k < alts.length; k++) alts[k].setAttribute('alt', alts[k].getAttribute('data-alt-' + lang) || alts[k].getAttribute('alt'));
    var t = root.getAttribute('data-title-' + lang); if (t) d.title = t;
    var btns = d.querySelectorAll('button[data-lang],a[data-lang]');
    for (var j = 0; j < btns.length; j++) {
      var on = btns[j].getAttribute('data-lang') === lang;
      btns[j].classList.toggle('is-active', on);
      btns[j].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
    var main = d.getElementById('vrc-gt'); if (main) main.setAttribute('data-lang', lang);
    if (typeof window.vrcSetCrestLanguage === 'function') window.vrcSetCrestLanguage(lang, null);
    try { localStorage.setItem(KEY, lang); localStorage.setItem('vrcCrestLanguage', lang); } catch (e) {}
  }
  function swap(lang) {
    if (root.getAttribute('data-lang') === lang) return;
    root.classList.add('i18n-fade');
    setTimeout(function () {
      apply(lang);
      requestAnimationFrame(function () { root.classList.remove('i18n-fade'); });
    }, 160);
  }
  d.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('button[data-lang],a[data-lang]');
    if (!b) return;
    e.preventDefault();
    swap(b.getAttribute('data-lang'));
  });
  apply(saved());
  requestAnimationFrame(function () { root.classList.remove('i18n-fade'); });
  window.vrcSetLang = swap;
})();
