(function () {
  document.documentElement.classList.add('js');

  // Hero MRI series: scan through the 16 slices once, when the band is first seen.
  var series = document.querySelector('.series');
  if (series) {
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { series.classList.add('play'); io.disconnect(); }
        });
      }, { threshold: 0.3 });
      io.observe(series);
    } else {
      series.classList.add('play');
    }
  }

  // Figure lightbox
  var dlg = document.getElementById('lightbox');
  if (dlg && typeof dlg.showModal === 'function') {
    var big = dlg.querySelector('img');
    var cap = dlg.querySelector('.lb-cap');
    var opener = null;
    document.querySelectorAll('button.zoom').forEach(function (b) {
      b.addEventListener('click', function () {
        var img = b.querySelector('img');
        big.src = b.getAttribute('data-full') || img.currentSrc || img.src;
        big.alt = img.alt;
        cap.textContent = img.alt;
        opener = b;
        dlg.showModal();
      });
    });
    dlg.querySelector('.lb-close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('close', function () { big.removeAttribute('src'); if (opener) opener.focus(); });
  } else {
    document.querySelectorAll('button.zoom').forEach(function (b) {
      b.addEventListener('click', function () {
        window.open(b.getAttribute('data-full') || b.querySelector('img').src, '_blank', 'noopener');
      });
    });
  }

  // Publication filter
  var bar = document.querySelector('.filters');
  if (bar) {
    var buttons = bar.querySelectorAll('button');
    var items = document.querySelectorAll('.pubs li[data-theme]');
    var groups = document.querySelectorAll('.pub-group');
    var status = document.getElementById('filter-status');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var want = btn.getAttribute('data-filter');
        buttons.forEach(function (x) { x.setAttribute('aria-pressed', x === btn ? 'true' : 'false'); });
        var shown = 0;
        items.forEach(function (li) {
          var ok = want === 'all' || li.getAttribute('data-theme') === want;
          li.hidden = !ok;
          if (ok) shown++;
        });
        groups.forEach(function (g) {
          var any = g.querySelectorAll('.pubs li[data-theme]:not([hidden])').length > 0;
          g.hidden = !any;
        });
        if (status) status.textContent = 'Showing ' + shown + ' of ' + items.length + ' papers.';
      });
    });
  }
})();
