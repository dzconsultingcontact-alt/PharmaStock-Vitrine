#!/usr/bin/env python3
"""Actualités du blog : une page par article, la rubrique « Actualités » du blog, le plan du site, le flux RSS
et le bloc « Actualités » de la page d'accueil, à partir des fichiers outils/articles/*.json.

Ajouter un article : déposer un fichier outils/articles/<adresse>.json (voir les fichiers existants), puis lancer
    python3 outils/vitrine_blog.py .
à la racine du site. Le script peut être relancé sans risque : il remplace les blocs qu'il a lui-même posés.

Format d'un article (français obligatoire, arabe conseillé : la page bascule en arabe avec le bouton du site) :
  slug, date (AAAA-MM-JJ), categorie / categorie_ar, titre / titre_ar, description / description_ar,
  chapo / chapo_ar, mots_cles, blocs : [{"t": "p"|"h2", "fr", "ar"} | {"t": "ul", "items": [{"fr", "ar"}]} | {"t": "cta"}],
  sources : [{"titre", "media", "date", "url"}], liens : ["/blog/…/", …] (articles à lire aussi).
Le texte des blocs peut contenir <strong>, <em> et <a href="/…">.
"""
import glob, html, json, os, re, sys
from datetime import date

RACINE = sys.argv[1] if len(sys.argv) > 1 else '.'
SITE = 'https://mapharmastock.com'
GABARIT = 'blog/inventaire-tournant-pharmacie/index.html'
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
MOIS_AR = ['يناير', 'فبراير', 'مارس', 'أبريل', 'ماي', 'يونيو', 'يوليوز', 'غشت', 'شتنبر', 'أكتوبر', 'نونبر', 'دجنبر']
ICONE = ('<svg class="ps-i" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path>'
         '<path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>')
RSS = '<link rel="alternate" type="application/rss+xml" title="Actualités PharmaStock" href="/blog/feed.xml">'
CTA = ('<div class="ps-cta-box"><p><strong>Essayez PharmaStock dans votre officine</strong>Stock, péremptions, commandes, crédit client, '
       'rappels patients et ordonnances dans une seule application, en français et en arabe.</p>\n'
       '<a class="ps-btn ps-btn-w" href="/#pionnieres">Demander une démo →</a></div>')

a = lambda s: html.escape(s, quote=True)  # attribut
lire = lambda p: open(os.path.join(RACINE, p), encoding='utf-8').read()


def ecrire(p, s):
    os.makedirs(os.path.dirname(os.path.join(RACINE, p)) or '.', exist_ok=True)
    open(os.path.join(RACINE, p), 'w', encoding='utf-8').write(s)


def date_fr(d):
    y, m, j = map(int, d.split('-'))
    return f"{j}{'er' if j == 1 else ''} {MOIS[m - 1]} {y}"


def date_ar(d):
    y, m, j = map(int, d.split('-'))
    return f'{j} {MOIS_AR[m - 1]} {y}'


def bloc(b, attr=''):
    ar = f' data-ar="{a(b["ar"])}"' if b.get('ar') else ''
    return f'<{b["t"]}{ar}{attr}>{b["fr"]}</{b["t"]}>'


def page(art, tous, gabarit):
    url = f'{SITE}/blog/{art["slug"]}/'
    titre_page = f'{art["titre"]} | Blog PharmaStock'
    titre_page_ar = f'{art.get("titre_ar", art["titre"])} | مدونة PharmaStock'
    tete = '\n'.join([
        f'<title>{html.escape(titre_page)}</title>',
        f'<meta name="description" content="{a(art["description"])}">',
        f'<meta name="ps-title-ar" content="{a(titre_page_ar)}">',
        f'<meta name="ps-desc-ar" content="{a(art.get("description_ar", art["description"]))}">',
        f'<meta name="keywords" content="{a(art.get("mots_cles", ""))}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<link rel="canonical" href="{url}">',
        RSS,
        '<meta property="og:type" content="article">',
        '<meta property="og:locale" content="fr_MA">',
        f'<meta property="og:title" content="{a(titre_page)}">',
        f'<meta property="og:description" content="{a(art["description"])}">',
        f'<meta property="og:url" content="{url}">',
        '<meta property="og:site_name" content="PharmaStock">',
        f'<meta property="article:published_time" content="{art["date"]}">',
        f'<meta property="article:modified_time" content="{art.get("modifie", art["date"])}">',
        f'<meta property="article:section" content="{a(art["categorie"])}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{a(titre_page)}">',
        f'<meta name="twitter:description" content="{a(art["description"])}">',
        '',
    ])
    s = gabarit
    i, j = s.index('<title>'), s.index('<link href="https://fonts.googleapis')
    s = s[:i] + tete + s[j:]
    posting = {
        '@context': 'https://schema.org', '@type': 'NewsArticle' if art.get('actualite', True) else 'BlogPosting',
        'headline': art['titre'], 'description': art['description'],
        'datePublished': art['date'], 'dateModified': art.get('modifie', art['date']), 'inLanguage': 'fr-MA',
        'mainEntityOfPage': url, 'articleSection': art['categorie'], 'keywords': art.get('mots_cles', ''),
        'author': {'@type': 'Organization', 'name': 'PharmaStock', 'url': SITE + '/'},
        'publisher': {'@type': 'Organization', 'name': 'PharmaStock — DZ Consulting', 'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/og-pharmastock.jpg'}},
        'image': SITE + '/assets/og-pharmastock.jpg',
        'citation': [x['url'] for x in art.get('sources', [])],
    }
    fil = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE + '/blog/'},
        {'@type': 'ListItem', 'position': 3, 'name': art['titre'], 'item': url}]}
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    s = re.sub(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"BlogPosting".*?</script>',
               lambda m: f'<script type="application/ld+json">{js(posting)}</script>', s, count=1, flags=re.S)
    s = re.sub(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"BreadcrumbList".*?</script>',
               lambda m: f'<script type="application/ld+json">{js(fil)}</script>', s, count=1, flags=re.S)

    corps = []
    n_h2 = 0
    for b in art['blocs']:
        if b['t'] == 'cta':
            corps.append(CTA)
        elif b['t'] == 'ul' or b['t'] == 'ol':
            corps.append(f'<{b["t"]}>\n' + '\n'.join(bloc({'t': 'li', **x}) for x in b['items']) + f'\n</{b["t"]}>')
        else:
            if b['t'] == 'h2':
                n_h2 += 1
            corps.append(bloc(b))
    if art.get('sources'):
        corps.append('<h2 data-ar="المصادر">Sources</h2>')
        corps.append('<ul class="ps-sources">\n' + '\n'.join(
            f'<li><a href="{a(x["url"])}" target="_blank" rel="noopener">{html.escape(x["titre"])}</a> — {html.escape(x["media"])}'
            f'{", " + html.escape(date_fr(x["date"])) if x.get("date") else ""}</li>' for x in art['sources']) + '\n</ul>')
        corps.append('<p class="ps-note-src" style="font-size:.9rem;font-style:italic" data-ar="هذا المقال ملخص لمعلومات منشورة؛ النصوص الرسمية هي المرجع.">'
                     "Cet article résume des informations publiées ; seuls les textes officiels font foi.</p>")
    corps.append(CTA)
    autres = [x for x in tous if x['slug'] != art['slug']][:3]
    liens = [(f'/blog/{x["slug"]}/', x['titre']) for x in autres] + [(u, t) for u, t in art.get('liens', [])]
    if liens:
        corps.append('<h2 data-ar="اقرأ أيضا">À lire aussi</h2>')
        corps.append('<ul>' + ''.join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for u, t in liens) + '</ul>')
    corps.append('<p><a href="/blog/" data-ar="← كل مقالات المدونة">← Tous les articles du blog</a></p>')

    hero = (f'<main id="contenu"><section class="ps-hero"><div class="ps-in">\n'
            f'  <div class="ps-crumb"><a href="/">Accueil</a> › <a href="/blog/">Blog</a> › <span data-ar="{a(art.get("categorie_ar", ""))}">{html.escape(art["categorie"])}</span></div>\n'
            f'  <h1 data-ar="{a(art.get("titre_ar", ""))}">{html.escape(art["titre"])}</h1>\n'
            f'  <p data-ar="{a(art.get("chapo_ar", ""))}">{art["chapo"]}</p>\n'
            f'  <p class="ps-meta" data-ar="{a(art.get("categorie_ar", "") + " · فريق PharmaStock · " + date_ar(art["date"]))}">'
            f'{html.escape(art["categorie"])} · Équipe PharmaStock · <time datetime="{art["date"]}">{date_fr(art["date"])}</time></p>\n'
            f'</div></section>\n<section class="ps-sec"><div class="ps-in"><article class="ps-prose">\n' + '\n\n'.join(corps) +
            '\n</article></div></section></main>')
    i, j = s.index('<main id="contenu">'), s.index('</main>') + len('</main>')
    return s[:i] + hero + s[j:]


def poser(s, debut, fin, contenu, avant=None):
    """Remplace le bloc entre les marqueurs, ou le pose avant `avant` la première fois."""
    if debut in s:
        i, j = s.index(debut), s.index(fin) + len(fin)
        return s[:i] + debut + contenu + fin + s[j:]
    k = s.index(avant)
    return s[:k] + debut + contenu + fin + '\n' + s[k:]


def carte(x, titre_balise='h3'):
    return (f'<div class="ps-card"><span class="ps-new" style="background:#FEF3E2;color:#9A5B0B" data-ar="{a(x.get("categorie_ar", ""))}">{html.escape(x["categorie"])} · {date_fr(x["date"])}</span>'
            f'<div class="ps-ico">{ICONE}</div><{titre_balise}><a href="/blog/{x["slug"]}/" data-ar="{a(x.get("titre_ar", ""))}">{html.escape(x["titre"])}</a></{titre_balise}>'
            f'<p data-ar="{a(x.get("description_ar", ""))}">{html.escape(x["description"])}</p><a class="ps-lire" href="/blog/{x["slug"]}/" data-ar="اقرأ المقال ←">Lire l\'article →</a></div>')


def main():
    arts = [json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(RACINE, 'outils/articles/*.json'))]
    arts.sort(key=lambda x: (x['date'], x.get('rang', 0), x['slug']), reverse=True)  # rang : ordre entre articles du même jour
    if not arts:
        print('Aucun article.'); return
    gabarit = lire(GABARIT)
    for x in arts:
        ecrire(f'blog/{x["slug"]}/index.html', page(x, arts, gabarit))

    # Rubrique « Actualités » en tête du blog
    b = lire('blog/index.html')
    rub = ('<h2 class="ps-h2" id="cat-actu" style="font-size:1.4rem;margin:0 0 18px;scroll-margin-top:90px" data-ar="المستجدات">Actualités</h2>'
           '<div class="ps-grid ps-guides">' + ''.join(carte(x) for x in arts) + '</div>'
           '<p style="margin:10px 0 40px"><a href="/blog/feed.xml" data-ar="تابعوا المستجدات (RSS)">Suivre les actualités (flux RSS)</a></p>\n')
    b = poser(b, '<!-- ACTUS (posé par vitrine_blog.py) -->', '<!-- /ACTUS -->', rub, avant='<h2 class="ps-h2" id="cat-0"')
    b = b.replace('id="cat-0" style="font-size:1.4rem;margin:0 0 18px', 'id="cat-0" style="font-size:1.4rem;margin:40px 0 18px')
    if 'href="#cat-actu"' not in b:
        b = b.replace('<ul class="ps-villes" style="margin-top:14px">', '<ul class="ps-villes" style="margin-top:14px"><li><a href="#cat-actu" data-ar="المستجدات">Actualités</a></li>', 1)
    if RSS not in b:
        b = b.replace('</head>', RSS + '</head>', 1)
    b = b.replace('<h1>Blog : la gestion de pharmacie au Maroc</h1>', '<h1>Blog : actualités et gestion de pharmacie au Maroc</h1>')
    b = b.replace('<p>Stock, péremptions, commandes, rentabilité, crédit client, fidélisation des patients et digitalisation : des articles pratiques pour mieux gérer votre officine.</p>',
                  '<p>Actualités du médicament au Maroc (prix, réglementation, saison) et articles pratiques pour mieux gérer votre officine : stock, péremptions, commandes, rentabilité, crédit client et fidélisation.</p>')
    m = re.search(r'(<script type="application/ld\+json">)(\{"@context":"https://schema.org","@type":"Blog".*?)(</script>)', b, re.S)
    if m:
        blog = json.loads(m.group(2))
        urls = {p['url'] for p in blog.get('blogPost', [])}
        nouveaux = [{'@type': 'BlogPosting', 'headline': x['titre'], 'url': f'{SITE}/blog/{x["slug"]}/', 'datePublished': x['date']} for x in arts if f'{SITE}/blog/{x["slug"]}/' not in urls]
        blog['blogPost'] = nouveaux + blog.get('blogPost', [])
        b = b[:m.start(2)] + json.dumps(blog, ensure_ascii=False, separators=(',', ':')) + b[m.end(2):]
    ecrire('blog/index.html', b)

    # Plan du site
    sm = lire('sitemap.xml')
    jour = max(x.get('modifie', x['date']) for x in arts)
    for x in arts:
        loc = f'{SITE}/blog/{x["slug"]}/'
        ligne = f'  <url><loc>{loc}</loc><lastmod>{x.get("modifie", x["date"])}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>'
        if f'<loc>{loc}</loc>' in sm:
            sm = re.sub(rf'  <url><loc>{re.escape(loc)}</loc>.*?</url>', ligne, sm)
        else:
            sm = sm.replace('</urlset>', ligne + '\n</urlset>')
    for loc in (f'{SITE}/blog/', f'{SITE}/'):
        sm = re.sub(rf'(<url><loc>{re.escape(loc)}</loc><lastmod>)[^<]*', rf'\g<1>{jour}', sm)
    ecrire('sitemap.xml', sm)

    # Flux RSS
    items = ''.join(
        f'<item><title>{html.escape(x["titre"])}</title><link>{SITE}/blog/{x["slug"]}/</link><guid>{SITE}/blog/{x["slug"]}/</guid>'
        f'<pubDate>{date.fromisoformat(x["date"]).strftime("%a, %d %b %Y")} 08:00:00 +0100</pubDate><category>{html.escape(x["categorie"])}</category>'
        f'<description>{html.escape(x["description"])}</description></item>\n' for x in arts)
    ecrire('blog/feed.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
           f'<title>Actualités PharmaStock — la pharmacie au Maroc</title><link>{SITE}/blog/</link>'
           f'<atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>'
           '<description>Réglementation, saison et gestion d\'officine : les actualités utiles aux pharmaciens au Maroc.</description>'
           f'<language>fr-MA</language>\n{items}</channel></rss>\n')

    # Accueil : les 3 dernières actualités, avant la FAQ
    s = lire('index.html')
    cartes = ''.join(
        f'<a class="actu-c sr" href="/blog/{x["slug"]}/"><small data-ar="{a(x.get("categorie_ar", "") + " · " + date_ar(x["date"]))}">{html.escape(x["categorie"])} · {date_fr(x["date"])}</small>'
        f'<b data-ar="{a(x.get("titre_ar", ""))}">{html.escape(x["titre"])}</b><span data-ar="{a(x.get("description_ar", ""))}">{html.escape(x["description"])}</span></a>' for x in arts[:3])
    bloc_accueil = ('\n<section id="actualites" class="sec" style="padding-top:20px">\n<style>'
                    '.actu-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}'
                    '.actu-c{display:flex;flex-direction:column;gap:10px;padding:26px;border:1px solid var(--line);border-radius:18px;background:#fff;text-decoration:none;color:var(--ink);transition:transform .3s,box-shadow .3s,border-color .3s}'
                    '.actu-c:hover{transform:translateY(-5px);box-shadow:0 24px 50px -18px rgba(11,27,43,.25);border-color:#9FCFCB}'
                    '.actu-c small{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--acc)}'
                    '.actu-c b{font-size:1.12rem;line-height:1.35;font-weight:600}.actu-c span{color:var(--mute);line-height:1.6;font-size:.95rem}'
                    '.actu-more{display:inline-block;margin-top:24px;font-weight:600;color:var(--acc)}</style>\n'
                    '<div class="wrap">\n<div class="sec-h sr">\n'
                    '<h2 class="h2 serif" data-ar="مستجدات الصيدلية في المغرب">Actualités de la pharmacie au Maroc</h2>\n'
                    '<p data-ar="الأسعار والتنظيم وموسم الأمراض وتسيير الصيدلية: ما يتغير بالنسبة لكم، مع مصادره.">Prix, réglementation, saison et gestion d\'officine : ce qui change pour vous, avec les sources.</p>\n'
                    f'</div>\n<div class="actu-g">{cartes}</div>\n'
                    '<a class="actu-more" href="/blog/" data-ar="كل المستجدات ←">Toutes les actualités →</a>\n</div>\n</section>\n')
    s = poser(s, '<!-- ACTUALITES (posé par vitrine_blog.py) -->', '<!-- /ACTUALITES -->', bloc_accueil, avant='<section id="faq"')
    if RSS not in s:
        s = s.replace('</head>', RSS + '</head>', 1)
    ecrire('index.html', s)
    print(f'{len(arts)} article(s) : pages, blog, sitemap, flux RSS et accueil à jour.')


if __name__ == '__main__':
    main()
