/* PharmaStock — site vitrine : bandeau défilant, bouton WhatsApp, formulaires de demande, choix de langue FR / العربية */
(function () {
  var API = 'https://api.mapharmastock.com/api';
  var WA = '33638557513';
  var CLE_LANG = 'ps-site-lang';

  function langue() {
    try {
      var m = /[?&]lang=(fr|ar)\b/.exec(location.search);
      if (m) { localStorage.setItem(CLE_LANG, m[1]); return m[1]; }
      return localStorage.getItem(CLE_LANG) === 'ar' ? 'ar' : 'fr';
    } catch (e) { return 'fr'; }
  }
  var SCRIPT = document.currentScript;
  var LANG_OFF = !!(SCRIPT && SCRIPT.getAttribute('data-lang') === 'off');
  var LANG = LANG_OFF ? 'fr' : langue();
  window.PS_LANG = LANG;

  function lienWa(texte) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(texte); }
  var MSG_WA = LANG === 'ar' ? 'السلام عليكم، أود معرفة المزيد عن PharmaStock لصيدليتي.' : "Bonjour, je souhaite en savoir plus sur PharmaStock pour ma pharmacie.";

  /* Thème « Officine » : bandeau défilant en haut de chaque page (la page d'accueil a le sien) */
  function bandeau() {
    if (document.querySelector('.band, .ps-band')) return;
    var items = [
      ['Base des médicaments du Maroc', 'قاعدة الأدوية المغربية'],
      ['Réception par scan DataMatrix', 'الاستلام بمسح DataMatrix'],
      ['Crédit client', 'ديون الزبناء'],
      ['Marketplace entre pharmacies', 'سوق بين الصيدليات'],
      ['Mode hors ligne', 'العمل بدون إنترنت'],
      ['Interface en arabe', 'الواجهة بالعربية']
    ];
    var ar = LANG === 'ar', html = '';
    for (var k = 0; k < 2; k++) items.forEach(function (t) { html += '<span>' + (ar ? t[1] : t[0]) + '</span><i>✦</i>'; });
    var s = document.createElement('div');
    s.className = 'ps-band'; s.setAttribute('aria-hidden', 'true'); s.setAttribute('data-notranslate', '');
    s.innerHTML = '<div class="ps-mq">' + html + '</div>';
    document.body.insertBefore(s, document.body.firstChild);
  }

  function boutonWhatsApp() {
    if (document.querySelector('.ps-wa')) return;
    var a = document.createElement('a');
    a.className = 'ps-wa'; a.href = lienWa(MSG_WA); a.target = '_blank'; a.rel = 'noopener';
    a.setAttribute('aria-label', 'WhatsApp PharmaStock');
    a.innerHTML = '<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="#fff" d="M16 3C8.8 3 3 8.7 3 15.8c0 2.3.6 4.5 1.8 6.4L3 29l7-1.8c1.8 1 3.9 1.5 6 1.5 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm0 23.4c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.1 1.1 1.1-4-.3-.4a10.4 10.4 0 0 1-1.6-5.6C5.3 10 10.1 5.3 16 5.3s10.7 4.7 10.7 10.5S21.9 26.4 16 26.4zm5.9-7.8c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.7 8.7 0 0 1-4.3-3.7c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.5l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.1 1.1-1.1 2.7 1.2 3.1 1.3 3.3c.2.2 2.3 3.5 5.6 4.9 2.1.9 2.9 1 4 .8.6-.1 1.9-.8 2.2-1.5.3-.8.3-1.4.2-1.5-.1-.2-.3-.3-.6-.4z"/></svg><span>' + (LANG === 'ar' ? 'واتساب' : 'WhatsApp') + '</span>';
    document.body.appendChild(a);
  }

  /* Formulaires : <form data-ps-lead="DEMO|PIONNIERE|ESSAI|CONTACT"> avec des champs name=prenom, nom, tel, email, pharmacie, ville, message */
  function formulaires() {
    document.querySelectorAll('form[data-ps-lead]').forEach(function (f) {
      if (f.__ps) return; f.__ps = true;
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var d = { type: f.getAttribute('data-ps-lead'), page: location.pathname, langue: LANG };
        new FormData(f).forEach(function (v, k) { d[k === 'site_web' ? 'siteWeb' : k] = String(v).trim(); });
        var msg = f.querySelector('.ps-msg'), btn = f.querySelector('button[type=submit]');
        var ar = LANG === 'ar';
        if (!d.tel && !d.email) { msg.className = 'ps-msg err'; msg.textContent = ar ? 'المرجو إدخال رقم الهاتف أو البريد الإلكتروني.' : 'Indiquez au moins un téléphone ou un email.'; return; }
        var texteBtn = btn.textContent; btn.disabled = true; btn.textContent = ar ? 'جارٍ الإرسال…' : 'Envoi en cours…';
        var resume = (ar ? 'السلام عليكم، ' : 'Bonjour, ') + (d.type === 'PIONNIERE' ? (ar ? 'أرغب في الانضمام إلى برنامج الصيدليات الرائدة.' : 'je souhaite rejoindre le programme Pharmacies Pionnières.') : (ar ? 'أرغب في عرض توضيحي لـ PharmaStock.' : 'je souhaite une démonstration de PharmaStock.')) +
          '\n' + [d.prenom, d.nom].filter(Boolean).join(' ') + (d.pharmacie ? ' — ' + d.pharmacie : '') + (d.ville ? ' (' + d.ville + ')' : '') + (d.tel ? '\n' + d.tel : '') + (d.message ? '\n' + d.message : '');
        fetch(API + '/prospects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
          .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) throw new Error(j.message || ''); return j; }); })
          .then(function () {
            f.querySelectorAll('input,select,textarea,button[type=submit]').forEach(function (x) { x.disabled = true; });
            msg.className = 'ps-msg ok';
            msg.innerHTML = (ar ? '<b>شكرا!</b> سيتصل بكم فريقنا خلال 24 ساعة. للحصول على رد أسرع:' : '<b>Merci !</b> Notre équipe vous recontacte sous 24 h. Pour aller plus vite :') +
              '<br><a class="ps-btn ps-btn-w" style="margin-top:10px" target="_blank" rel="noopener" href="' + lienWa(resume) + '">' + (ar ? 'أرسل على واتساب' : 'Écrire sur WhatsApp') + '</a>';
            btn.textContent = ar ? 'تم الإرسال ✓' : 'Demande envoyée ✓';
            if (window.gtag) window.gtag('event', 'generate_lead', { lead_type: d.type });
          })
          .catch(function (err) {
            btn.disabled = false; btn.textContent = texteBtn;
            msg.className = 'ps-msg err';
            msg.innerHTML = (err.message || (ar ? 'تعذر الإرسال.' : "L'envoi n'a pas abouti.")) + ' ' + (ar ? 'يمكنكم مراسلتنا مباشرة على ' : 'Vous pouvez nous écrire directement sur ') +
              '<a target="_blank" rel="noopener" href="' + lienWa(resume) + '">WhatsApp</a>.';
          });
      });
    });
  }

  function boutonsLangue() {
    var suivant = LANG === 'ar' ? 'fr' : 'ar';
    var libelle = LANG === 'ar' ? 'Français' : 'العربية';
    var titre = LANG === 'ar' ? 'Version française' : 'النسخة العربية';
    function creer(cls) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = cls; b.textContent = libelle; b.title = titre; b.setAttribute('aria-label', titre);
      b.setAttribute('data-notranslate', '');
      b.onclick = function () {
        try { localStorage.setItem(CLE_LANG, suivant); } catch (e) { }
        var u = new URL(location.href); u.searchParams.delete('lang'); if (suivant === 'ar') u.searchParams.set('lang', 'ar');
        location.href = u.toString();
      };
      return b;
    }
    var na = document.querySelector('.nav-actions');
    if (na && !na.querySelector('.ps-lang')) na.insertBefore(creer('ps-lang'), na.firstChild);
    var mm = document.querySelector('#mobileMenu .mm-ctas') || document.getElementById('mobileMenu');
    if (mm && !mm.querySelector('.ps-lang')) mm.appendChild(creer('ps-lang ps-lang-m'));
  }

  function arabe() {
    if (LANG !== 'ar') return;
    document.documentElement.lang = 'ar';
    document.documentElement.dir = 'rtl';
    var l = document.createElement('link'); l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap';
    document.head.appendChild(l);
    var s = document.createElement('script'); s.src = '/assets/ps-ar.js?v=5'; s.defer = true;
    document.head.appendChild(s);
  }

  arabe();
  function init() { bandeau(); boutonWhatsApp(); formulaires(); if (!LANG_OFF) boutonsLangue(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
