/* Phóng to ảnh trong .sat-gallery: bấm ảnh, ← → để chuyển, Esc để đóng. */
(function () {
  var d = document, box, img, cap, list = [], i = 0;
  function lang() { return d.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'vi'; }
  function show(k) {
    i = (k + list.length) % list.length;
    var a = list[i], c = a.parentNode.querySelector('figcaption');
    img.src = a.getAttribute('href');
    img.alt = c ? c.textContent : '';
    cap.textContent = c ? (c.getAttribute('data-' + lang()) || c.textContent) : '';
  }
  function close() { box.classList.remove('is-open'); d.body.style.overflow = ''; }
  function build() {
    box = d.createElement('div'); box.className = 'sat-lightbox'; box.setAttribute('role', 'dialog');
    box.innerHTML = '<button class="sat-lb-x" aria-label="Đóng / Close">×</button><button class="sat-lb-prev" aria-label="Trước / Previous">‹</button><figure><img alt=""><figcaption></figcaption></figure><button class="sat-lb-next" aria-label="Sau / Next">›</button>';
    d.body.appendChild(box);
    img = box.querySelector('img'); cap = box.querySelector('figcaption');
    box.addEventListener('click', function (e) {
      if (e.target.closest('.sat-lb-prev')) show(i - 1);
      else if (e.target.closest('.sat-lb-next')) show(i + 1);
      else if (e.target === box || e.target.closest('.sat-lb-x')) close();
    });
    d.addEventListener('keydown', function (e) {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close(); else if (e.key === 'ArrowLeft') show(i - 1); else if (e.key === 'ArrowRight') show(i + 1);
    });
  }
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('.sat-gallery a[data-zoom]');
    if (!a) return;
    e.preventDefault();
    if (!box) build();
    list = [].slice.call(a.closest('.sat-gallery').querySelectorAll('a[data-zoom]'));
    show(list.indexOf(a));
    box.classList.add('is-open'); d.body.style.overflow = 'hidden';
  });
})();
