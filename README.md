# PharmaStock — site vitrine (mapharmastock.com)

Site statique servi depuis `public_html` sur l'hébergement Hostinger.

- `develop` : branche de travail
- `main` : branche déployée en production

Non versionné : `api/notify.php` (contient un jeton), à conserver sur le serveur.

## Menu du site

Le menu (barre du haut et menu du téléphone) est le même sur toutes les pages. Il est décrit une seule fois dans
`outils/vitrine_menu.py` : pour ajouter, retirer ou renommer un lien, modifiez la liste en tête de ce fichier puis lancez
`python3 outils/vitrine_menu.py .` à la racine du site ; le script remet le menu à jour dans chaque page.
Son apparence est dans `assets/ps-site.css` (bloc « MENU DU SITE »).
