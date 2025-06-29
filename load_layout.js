(function(){
  const script = document.currentScript;
  const base = script.dataset.base || '';
  function upgradeLayout(){
    if (window.componentHandler) {
      const layout = document.querySelector('.mdl-layout');
      if (layout) {
        layout.classList.remove('is-upgraded');
        layout.removeAttribute('data-upgraded');
        componentHandler.upgradeElement(layout);
      }
    }
  }
  function attachUmlListeners(){
    document.querySelectorAll('.uml-link').forEach(l => {
      l.addEventListener('click', e => {
        e.preventDefault();
        if (typeof window.toggleUml === 'function') {
          window.toggleUml();
        }
      });
    });
  }
  function attachLangListener(){
    const link = document.querySelector('.lang-link');
    if (!link) return;
    link.addEventListener('click', e => {
      e.preventDefault();
      const html = document.documentElement;
      const isRu = html.lang === 'ru';
      html.lang = isRu ? 'en' : 'ru';
      link.textContent = isRu ? 'RU' : 'EN';
      document.querySelectorAll('[data-en]').forEach(el => {
        if (isRu) {
          el.dataset.ru = el.textContent;
          el.textContent = el.dataset.en;
        } else if (el.dataset.ru) {
          el.textContent = el.dataset.ru;
        }
      });
    });
  }
  fetch(base + 'header.html').then(r => r.text()).then(t => {
    const placeholder = document.getElementById('header-placeholder');
    placeholder.outerHTML = t;
    attachUmlListeners();
    attachLangListener();
    upgradeLayout();
  });
  fetch(base + 'footer.html').then(r => r.text()).then(t => {
    const footer = document.getElementById('footer-placeholder');
    footer.outerHTML = t;
    if (window.componentHandler) componentHandler.upgradeDom();
  });
})();
