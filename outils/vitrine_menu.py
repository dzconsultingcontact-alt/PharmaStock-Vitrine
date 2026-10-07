#!/usr/bin/env python3
"""Menu du site vitrine : le même sur toutes les pages.

Le menu est décrit une seule fois ici (liens, libellés français et arabes). Le script le pose dans chaque page HTML
(à la place de l'ancien, quel que soit le gabarit de la page), met à jour la feuille de style et le script communs,
et peut être relancé sans risque : il remplace alors le bloc qu'il a lui-même posé.

Usage : python3 outils/vitrine_menu.py . (à la racine du site)
"""
import glob, os, re, sys

RACINE = sys.argv[1]
VERSION = '9'   # ?v= des fichiers communs (ps-site.css, ps-site.js)

# (clé, adresse, libellé, arabe, classe qui retire le lien quand la place manque)
LIENS = [
    ('fonctionnalites', '/fonctionnalites.html', 'Fonctionnalités', 'الوظائف', ''),
    ('journee', '/#journee', 'Une journée', 'يوم في الصيدلية', 'psn-o1'),
    ('reseau', '/#reseau', 'Réseau', 'الشبكة', 'psn-o3'),
    ('offres', '/offres.html', 'Offres', 'العروض', ''),
    ('fournisseurs', '/fournisseurs/', 'Fournisseurs', 'الموردون', ''),
    ('garde', '/pharmacie-de-garde/', 'Pharmacies de garde', 'صيدليات الحراسة', ''),
    ('blog', '/blog/', 'Blog', 'المدونة', 'psn-o2'),
]
MOBILE = [
    ('fonctionnalites', '/fonctionnalites.html', 'Fonctionnalités', 'الوظائف'),
    ('journee', '/#journee', 'Une journée', 'يوم في الصيدلية'),
    ('reseau', '/#carte', 'Réseau', 'الشبكة'),
    ('pionnieres', '/#pionnieres', 'Offre 30 premières pharmacies', 'عرض أول 30 صيدلية'),
    ('offres', '/offres.html', 'Offres', 'العروض'),
    ('fournisseurs', '/fournisseurs/', 'Espace fournisseurs', 'فضاء الموردين'),
    ('garde', '/pharmacie-de-garde/', 'Pharmacies de garde', 'صيدليات الحراسة'),
    ('guides', '/guides/', 'Guides', 'الأدلة'),
    ('blog', '/blog/', 'Blog', 'المدونة'),
    ('apropos', '/qui-sommes-nous.html', 'Qui sommes-nous', 'من نحن'),
    ('contact', '/contact.html', 'Contact', 'اتصل بنا'),
]
DEBUT, FIN = '<!-- MENU PharmaStock (commun à toutes les pages, posé par vitrine_menu.py) -->', '<!-- /MENU PharmaStock -->'
SCRIPT = ("<script>function psMenu(f){var m=document.getElementById('mobileMenu'),h=document.getElementById('hamburger');if(!m||!h)return;"
          "var o=typeof f==='boolean'?f:!m.classList.contains('open');m.classList.toggle('open',o);h.classList.toggle('active',o);h.setAttribute('aria-expanded',o);"
          "document.documentElement.style.overflow=o?'hidden':'';}"
          "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('#mobileMenu a');if(a)psMenu(false);});"
          "document.addEventListener('keydown',function(e){if(e.key==='Escape')psMenu(false);});</script>")


def page_courante(chemin):
    """Clé du lien à mettre en évidence pour cette page."""
    c = chemin.replace(os.sep, '/')
    for prefixe, cle in (('fonctionnalites.html', 'fonctionnalites'), ('offres.html', 'offres'), ('fournisseurs/', 'fournisseurs'),
                         ('pharmacie-de-garde/', 'garde'), ('blog/', 'blog'), ('guides/', 'guides'), ('contact.html', 'contact'), ('qui-sommes-nous.html', 'apropos')):
        if c.startswith(prefixe):
            return cle
    return ''


def menu(chemin):
    accueil = chemin == 'index.html'
    ici = page_courante(chemin)
    # Sur la page d'accueil, les liens vers ses propres sections restent des ancres (pas de rechargement)
    adresse = lambda u: u[1:] if accueil and u.startswith('/#') else u
    courant = lambda cle: ' aria-current="page"' if cle == ici else ''
    liens = '\n'.join(f'<a{" class=" + chr(34) + cls + chr(34) if cls else ""} href="{adresse(u)}"{courant(cle)} data-ar="{ar}">{fr}</a>' for cle, u, fr, ar, cls in LIENS)
    mobile = '\n'.join(f'<div class="psn-mm-item"><a href="{adresse(u)}"{courant(cle)} data-ar="{ar}">{fr}</a></div>' for cle, u, fr, ar in MOBILE)
    return f'''{DEBUT}
<header class="psn">
<div class="psn-in">
<a class="psn-logo" href="/" aria-label="PharmaStock, accueil"><i><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7FD1C7" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></i><span data-notranslate>PharmaStock</span></a>
<div class="psn-links" role="navigation" aria-label="Navigation principale">
{liens}
</div>
<div class="psn-actions"><a class="psn-login" href="https://app.mapharmastock.com/login" data-ar="تسجيل الدخول">Se connecter</a><a class="psn-cta" href="/inscription/" data-ar="تجربة مجانية">Essai gratuit</a></div>
<button class="psn-hb" id="hamburger" type="button" aria-label="Menu" aria-controls="mobileMenu" aria-expanded="false" onclick="psMenu()"><span></span><span></span><span></span></button>
</div>
</header>
<div class="psn-mm" id="mobileMenu" aria-label="Menu mobile">
{mobile}
<div class="psn-mm-ctas"><a href="/inscription/" class="psn-mm-cta1" data-ar="ابدأ التجربة المجانية">Démarrer l'essai gratuit</a><a href="https://app.mapharmastock.com/login" class="psn-mm-cta2" data-ar="تسجيل الدخول">Se connecter</a></div>
</div>
{SCRIPT}
{FIN}'''


def poser(chemin, html):
    """Remplace le menu de la page, quel que soit son gabarit. Rend (nouveau html, gabarit reconnu)."""
    bloc = menu(chemin)
    if DEBUT in html and FIN in html:
        a, b = html.index(DEBUT), html.index(FIN) + len(FIN)
        return html[:a] + bloc + html[b:], 'déjà posé'
    # Gabarit récent (accueil, fonctionnalités) : <header class="nav"> … menu mobile … script du menu
    m = re.search(r'<header class="nav">[\s\S]*?</header>\s*<div class="mobile-menu" id="mobileMenu"[\s\S]*?\n</div>\s*<script>\s*function toggleMobile[\s\S]*?</script>', html)
    if m:
        return html[:m.start()] + bloc + html[m.end():], 'récent'
    # Ancien gabarit : bandeau d'annonce, barre de navigation à menus déroulants, menu mobile
    a = html.find('<!-- TOPBAR -->')
    m = re.search(r'<div class="mobile-menu" id="mobileMenu">[\s\S]*?\n</div>\n', html)
    if a >= 0 and m and m.start() > a and html.count('<nav>', a, m.start()) == 1:
        reste = html[m.end():]
        # Une page porte parfois un second menu mobile, resté d'une ancienne retouche : il part aussi
        reste = re.sub(r'\s*(?:<!-- (?:NAV|MOBILE MENU) -->\s*)*<div class="mobile-menu" id="mobileMenu">[\s\S]*?\n</div>\n', '\n', reste)
        return html[:a] + bloc + '\n' + reste, 'ancien'
    return html, None


def versions(html):
    return re.sub(r'(/assets/ps-site\.(?:css|js))\?v=\d+', r'\1?v=' + VERSION, html)


def main():
    pages = sorted(p for p in glob.glob('**/*.html', root_dir=RACINE, recursive=True))
    bilan = {}
    for p in pages:
        f = os.path.join(RACINE, p)
        avant = open(f, encoding='utf-8').read()
        apres, gabarit = poser(p, avant)
        if gabarit is None:
            print('  NON RECONNUE :', p); bilan['non reconnue'] = bilan.get('non reconnue', 0) + 1; continue
        apres = versions(apres)
        assert apres.count('id="mobileMenu"') == 1 and apres.count('id="hamburger"') == 1 and apres.count('<header class="psn">') == 1, p
        if apres != avant:
            open(f, 'w', encoding='utf-8').write(apres)
        bilan[gabarit] = bilan.get(gabarit, 0) + 1
    print(len(pages), 'pages :', bilan)


main()
