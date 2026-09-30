/* PharmaStock – widget « Trouver une pharmacie de garde » pour le site vitrine.
   Utilisation : <div id="ps-gardes"></div><script src="/garde-widget.js" defer></script> */
(function () {
  var API = 'https://api.mapharmastock.com/api/gardes';
  var AR = (function () { try { return (window.PS_LANG || localStorage.getItem('ps-site-lang')) === 'ar' && document.documentElement.dir === 'rtl'; } catch (e) { return false; } })();
  var VILLES = AR ? [['casablanca', 'الدار البيضاء'], ['rabat', 'الرباط'], ['marrakech', 'مراكش'], ['fes', 'فاس'], ['tanger', 'طنجة'], ['agadir', 'أكادير'], ['oujda', 'وجدة']]
    : [['casablanca', 'Casablanca'], ['rabat', 'Rabat'], ['marrakech', 'Marrakech'], ['fes', 'Fès'], ['tanger', 'Tanger'], ['agadir', 'Agadir'], ['oujda', 'Oujda']];
  var T = AR ? {
    titre: 'ابحث عن صيدلية الحراسة', sous: 'صيدليات مفتوحة بالنهار وبالليل و24/24 بالقرب منك.', ar: 'Trouver une pharmacie de garde',
    maintenant: 'مفتوحة الآن', nuit: 'ليل', h24: '24/24', toutes: 'الكل', pres: 'بالقرب مني', loc: 'تحديد الموقع…', plus: 'عرض المزيد',
    charg: 'جارٍ التحميل…', indispo: 'الخدمة غير متوفرة حاليا. أعد المحاولة بعد قليل.', aucune: 'لا توجد صيدلية لهذا الاختيار. جرّب « الكل ».',
    ouverte: 'مفتوحة الآن', iti: 'الاتجاهات', du: 'من', au: 'إلى', ville: 'المدينة', tri: 'الترتيب حسب المسافة',
    info: function (n, v) { return n + ' صيدلية مفتوحة الآن في ' + v + '. اتصل قبل التنقل. المصدر: '; }, et: ' وصيدليات شبكة PharmaStock.',
    autres: 'صيدلية الحراسة في: ', loc2: 'ar-MA'
  } : {
    titre: 'Trouver une pharmacie de garde', sous: 'Pharmacies ouvertes de jour, de nuit et 24h/24 près de chez vous.', ar: 'ابحث عن صيدلية الحراسة الأقرب إليك',
    maintenant: 'Ouvertes maintenant', nuit: 'Nuit', h24: '24h/24', toutes: 'Toutes', pres: 'Près de moi', loc: 'Localisation…', plus: 'Voir plus',
    charg: 'Chargement…', indispo: 'Service momentanément indisponible. Réessayez dans quelques instants.', aucune: 'Aucune pharmacie pour ce choix. Essayez « Toutes ».',
    ouverte: 'Ouverte maintenant', iti: 'Itinéraire', du: 'du', au: 'au', ville: 'Ville', tri: 'Trier par distance',
    info: function (n, v) { return n + ' pharmacie(s) ouverte(s) maintenant à ' + v + '. Appelez avant de vous déplacer. Source : '; }, et: ' et pharmacies du réseau PharmaStock.',
    autres: 'Pharmacie de garde à : ', loc2: 'fr-FR'
  };
  var TYPES = { JOUR: [AR ? 'نهار' : 'Jour', '#b45309', '#fef3c7'], NUIT: [AR ? 'ليل' : 'Nuit', '#3730a3', '#e0e7ff'], '24H': [AR ? '24/24' : '24h/24', '#6b21a8', '#f3e8ff'] };

  var css = '' +
    '.psg{scroll-margin-top:90px;font-family:inherit;max-width:1100px;margin:0 auto;padding:48px 16px;color:#0f172a}' +
    '.psg h2{font-size:clamp(1.6rem,3vw,2.2rem);margin:0 0 6px;font-weight:800;text-align:center}' +
    '.psg .psg-sous{text-align:center;color:#475569;margin:0 0 4px}.psg .psg-ar{text-align:center;color:#64748b;margin:0 0 24px;direction:rtl}' +
    '.psg-barre{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:20px}' +
    '.psg-barre select,.psg-barre button{font:inherit;padding:10px 14px;border-radius:10px;border:1px solid #cbd5e1;background:#fff;cursor:pointer;min-height:44px}' +
    '.psg-barre button.psg-actif{background:#0f766e;color:#fff;border-color:#0f766e}' +
    '.psg-grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}' +
    '.psg-carte{background:#fff;border:1px solid #e2e8f0;border-left:5px solid #16a34a;border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:6px;box-shadow:0 1px 2px rgba(15,23,42,.05)}' +
    '.psg-carte.psg-fermee{border-left-color:#cbd5e1}' +
    '.psg-carte h3{margin:0;font-size:1.05rem}.psg-q{color:#0f766e;font-weight:600;font-size:.9rem}.psg-adr{color:#475569;font-size:.9rem;margin:0}' +
    '.psg-tags{display:flex;gap:6px;flex-wrap:wrap}.psg-tag{font-size:.75rem;font-weight:700;padding:3px 8px;border-radius:999px}' +
    '.psg-act{display:flex;gap:8px;margin-top:auto;padding-top:8px}.psg-act a{flex:1;text-align:center;text-decoration:none;font-weight:600;padding:10px;border-radius:10px;font-size:.9rem}' +
    '.psg-tel{background:#16a34a;color:#fff;white-space:nowrap;flex:1.5!important}.psg-it{border:1px solid #cbd5e1;color:#0f172a}' +
    '.psg-info{text-align:center;color:#64748b;font-size:.85rem;margin-top:16px}.psg-info a{color:#0f766e}' +
    '.psg-vide{text-align:center;padding:30px;color:#475569;background:#f8fafc;border-radius:14px}' +
    '.psg-plus{display:block;margin:18px auto 0;font:inherit;padding:10px 18px;border-radius:10px;border:1px solid #0f766e;color:#0f766e;background:#fff;cursor:pointer}' +
    '.psg-villes{text-align:center;margin-top:14px;font-size:.9rem;color:#475569;line-height:2}.psg-villes a{color:#0f766e;font-weight:600;text-decoration:none;margin:0 6px;white-space:nowrap}.psg-villes a:hover{text-decoration:underline}' +
    '.psg[dir=rtl] .psg-carte{border-left:1px solid #e2e8f0;border-right:5px solid #16a34a}.psg[dir=rtl] .psg-carte.psg-fermee{border-right-color:#cbd5e1}.psg .psg-num{direction:ltr;unicode-bidi:embed}';

  function el(tag, attrs, html) { var e = document.createElement(tag); for (var k in attrs || {}) e.setAttribute(k, attrs[k]); if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function jour(d) { try { return new Date(d).toLocaleDateString(T.loc2, { weekday: 'short', day: 'numeric', month: 'short' }); } catch (e) { return ''; } }

  function init() {
    var racine = document.getElementById('ps-gardes');
    if (!racine) return;
    var st = el('style'); st.textContent = css; document.head.appendChild(st);
    var fixe = racine.getAttribute('data-ville');
    var ville = fixe || (function () { try { return localStorage.getItem('psg-ville') || 'casablanca'; } catch (e) { return 'casablanca'; } })();
    var sansTitre = racine.hasAttribute('data-sans-titre');
    var filtre = 'maintenant', pos = null, data = null, limite = 9;

    var box = el('section', { 'class': 'psg', id: 'pharmacie-de-garde', 'aria-labelledby': 'psg-titre', 'data-notranslate': '' });
    if (AR) box.setAttribute('dir', 'rtl');
    box.innerHTML = sansTitre ? '' : '<h2 id="psg-titre">' + T.titre + '</h2>' +
      '<p class="psg-sous">' + T.sous + '</p>' +
      '<p class="psg-ar" lang="' + (AR ? 'fr' : 'ar') + '" style="direction:' + (AR ? 'ltr' : 'rtl') + '">' + T.ar + '</p>';
    if (sansTitre) box.style.paddingTop = '24px';
    var barre = el('div', { 'class': 'psg-barre' });
    var sel = el('select', { 'aria-label': T.ville });
    VILLES.forEach(function (v) { var o = el('option', { value: v[0] }, v[1]); if (v[0] === ville) o.selected = true; sel.appendChild(o); });
    barre.appendChild(sel);
    var boutons = {};
    [['maintenant', T.maintenant], ['NUIT', T.nuit], ['24H', T.h24], ['tous', T.toutes]].forEach(function (f) {
      var b = el('button', { type: 'button' }, f[1]); b.onclick = function () { filtre = f[0]; limite = 9; majBoutons(); rendre(); };
      boutons[f[0]] = b; barre.appendChild(b);
    });
    var bPos = el('button', { type: 'button', title: T.tri }, T.pres);
    barre.appendChild(bPos);
    var liste = el('div', { 'class': 'psg-grille', 'aria-live': 'polite' });
    var plus = el('button', { type: 'button', 'class': 'psg-plus' }, T.plus);
    var info = el('p', { 'class': 'psg-info' });
    var villesLiens = el('p', { 'class': 'psg-villes' });
    villesLiens.innerHTML = T.autres + VILLES.map(function (v) { return '<a href="/pharmacie-de-garde/' + v[0] + '/">' + v[1] + '</a>'; }).join(' ');
    box.appendChild(barre); box.appendChild(liste); box.appendChild(plus); box.appendChild(info); box.appendChild(villesLiens);
    racine.appendChild(box);

    function majBoutons() { for (var k in boutons) boutons[k].className = k === filtre ? 'psg-actif' : ''; bPos.className = pos ? 'psg-actif' : ''; }
    plus.onclick = function () { limite += 12; rendre(); };
    sel.onchange = function () { ville = sel.value; try { if (!fixe) localStorage.setItem('psg-ville', ville); } catch (e) { } limite = 9; charger(); };
    bPos.onclick = function () {
      if (!navigator.geolocation) return;
      bPos.textContent = T.loc;
      navigator.geolocation.getCurrentPosition(function (p) { pos = { lat: p.coords.latitude, lng: p.coords.longitude }; bPos.textContent = T.pres; majBoutons(); charger(); },
        function () { bPos.textContent = T.pres; }, { timeout: 10000 });
    };

    function charger() {
      liste.innerHTML = '<div class="psg-vide">' + T.charg + '</div>'; plus.style.display = 'none';
      var url = API + '?ville=' + encodeURIComponent(ville) + (pos ? '&lat=' + pos.lat + '&lng=' + pos.lng : '');
      fetch(url).then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(function (d) { data = d; rendre(); })
        .catch(function () { liste.innerHTML = '<div class="psg-vide">' + T.indispo + '</div>'; info.textContent = ''; });
    }

    function rendre() {
      if (!data) return;
      var ps = (data.pharmacies || []).filter(function (p) { return filtre === 'tous' || (filtre === 'maintenant' ? p.ouverteMaintenant : p.typeGarde === filtre); });
      if (!ps.length) {
        liste.innerHTML = '<div class="psg-vide">' + T.aucune + '</div>'; plus.style.display = 'none';
      } else {
        liste.innerHTML = ps.slice(0, limite).map(function (p) {
          var t = TYPES[p.typeGarde] || TYPES['24H'];
          var it = p.latitude && p.longitude ? 'https://www.google.com/maps/dir/?api=1&destination=' + p.latitude + ',' + p.longitude
            : 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(p.nom + ' ' + (p.adresse || '') + ' ' + (data.villeNom || ''));
          var tel = (p.telephone || '').replace(/[^\d+]/g, '');
          return '<article class="psg-carte' + (p.ouverteMaintenant ? '' : ' psg-fermee') + '">' +
            '<div class="psg-tags"><span class="psg-tag" style="color:' + t[1] + ';background:' + t[2] + '">' + t[0] + '</span>' +
            (p.ouverteMaintenant ? '<span class="psg-tag" style="color:#166534;background:#dcfce7">' + T.ouverte + '</span>' : '') +
            (p.distanceKm != null ? '<span class="psg-tag" style="color:#334155;background:#f1f5f9">' + p.distanceKm + ' km</span>' : '') + '</div>' +
            '<h3>' + esc(p.nom) + '</h3>' + (p.quartier && p.quartier !== data.villeNom ? '<div class="psg-q">' + esc(p.quartier) + '</div>' : '') +
            '<p class="psg-adr">' + esc(p.adresse || '') + '</p>' +
            '<p class="psg-adr" style="font-size:.8rem">' + (AR ? '' : esc(p.horaires || '') + ' · ') + T.du + ' ' + jour(p.debut) + ' ' + T.au + ' ' + jour(p.fin) + '</p>' +
            '<div class="psg-act">' + (tel ? '<a class="psg-tel" href="tel:' + tel + '"><span class="psg-num">' + esc(p.telephone) + '</span></a>' : '') +
            '<a class="psg-it" href="' + it + '" target="_blank" rel="noopener">' + T.iti + '</a></div></article>';
        }).join('');
        plus.style.display = ps.length > limite ? 'block' : 'none';
      }
      var vn = (VILLES.filter(function (v) { return v[0] === data.ville; })[0] || [0, data.villeNom])[1];
      info.innerHTML = esc(T.info(data.nbOuvertes || 0, vn)) + '<a href="' + esc(data.sourceUrl) + '" target="_blank" rel="noopener">' + esc(data.source) + '</a>' + T.et;
    }

    majBoutons(); charger();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
