# Ölpreis und Krisennachrichten

Gruppenarbeit im Kurs **Web Mining und Datenvisualisierung**, WS 2026/27, Uni Mainz.

**Forschungsfrage:** Verbessern Krisennachrichten aus dem Web die Prognose des Ölpreises?

Wir holen tägliche Brent- und WTI-Preise per API und sammeln Nachrichten zu
Krisen (Nahost, Russland und Sanktionen, OPEC+, Schifffahrtswege). Daraus
berechnen wir pro Tag Menge und Stimmung der Krisenmeldungen und vergleichen
ein Prognosemodell nur mit Preisdaten gegen eines mit Nachrichten.

## Die sechs Schritte

Jeder Schritt ist ein eigenes Skript in `src/`. Jedes Skript speichert sein
Ergebnis als Datei, auf der der nächste Schritt aufbaut.

| Schritt | Skript | Was es tut | Ergebnis |
|---|---|---|---|
| 1 · Preisdaten holen | `prices.py` | Brent und WTI von FRED (Hauptquelle) und Yahoo Finance (Kontrolle), Abgleich beider Quellen | `data/processed/prices.csv` |
| 2 · Nachrichten sammeln | `news_guardian.py` | Guardian-Archiv ab 2015 (braucht API-Schlüssel) | `data/raw/guardian/` |
| | `news_live.py` | GDELT und Tagesschau, ab Ende November täglich starten | `data/raw/gdelt/`, `data/raw/tagesschau/` |
| | `news_crawler.py` | optional: eigener Scrapy-Crawler für eine News-Sitemap | `data/raw/crawler/` |
| 3 · Texte aufbereiten | `text_prep.py` | Duplikate entfernen, bereinigen, tokenisieren, Stimmung pro Artikel | `data/processed/articles.csv` |
| 4 · Features pro Tag | `features.py` | Preise und Nachrichten pro Tag zusammenführen, Nachrichten um 1 Tag versetzt | `data/processed/features.csv` |
| 5 · Modelle vergleichen | `models.py` | Baseline, Regression und Random Forest mit und ohne Nachrichten | `data/processed/model_results.csv` |
| 6 · Ergebnisse zeigen | `visualize.py` | Abbildungen für den Vortrag | `reports/figures/*.png` |

Gemeinsame Einstellungen (Zeitraum, Suchbegriffe, Ordner) stehen in
`src/config.py`. Stellen, an denen die Gruppe noch entscheiden muss, sind im
Code mit `TODO` markiert.

## Ordner

```
data/raw/         Rohdaten, genau so, wie sie von der Quelle kommen
data/processed/   aufbereitete Tabellen der Schritte 1, 3, 4, 5
notebooks/        Jupyter-Notebooks zum Ausprobieren
reports/figures/  Abbildungen für die Folien
src/              die Skripte
```

Die Ordner `data/raw` und `data/processed` werden **nicht** auf GitHub
hochgeladen (siehe `.gitignore`). Das Repo ist öffentlich, und Artikeltexte
von Guardian und Tagesschau dürfen wir nicht veröffentlichen. Jedes
Gruppenmitglied erzeugt die Daten selbst, indem es die Skripte startet.

## Einrichten (einmalig)

Du brauchst [Python 3.11 oder neuer](https://www.python.org/downloads/) und
[Git](https://git-scm.com/downloads). Die Befehle sind für Windows
(Eingabeaufforderung oder PowerShell); auf Mac/Linux steht die Variante dahinter.

```bash
# 1. Repo herunterladen und hineinwechseln
git clone https://github.com/sohrabschafaq/oelpreis-webmining.git
cd oelpreis-webmining

# 2. Virtuelle Umgebung anlegen und aktivieren
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate

# 3. Pakete installieren
pip install -r requirements.txt
```

**API-Schlüssel:** Kopiere `.env.example` und nenne die Kopie `.env`. Trage
dort deine kostenlosen Schlüssel ein (Links stehen in der Datei). Die `.env`
bleibt auf deinem Rechner und wird nie hochgeladen. **Schlüssel niemals direkt
in den Code schreiben**, denn das Repo ist öffentlich.

## Skripte starten

Immer aus dem Hauptordner des Repos, mit aktivierter virtueller Umgebung:

```bash
python src/prices.py
python src/news_guardian.py
python src/news_live.py
python src/text_prep.py
python src/features.py
python src/models.py
python src/visualize.py
```

## Zusammenarbeiten mit Git (Kurzfassung)

```bash
git pull                         # neueste Version holen, bevor du anfängst
git checkout -b mein-thema       # eigenen Zweig (Branch) für deine Änderung anlegen
# ... Dateien bearbeiten ...
git add src/prices.py            # Änderungen vormerken
git commit -m "Preis-Abgleich verbessert"
git push -u origin mein-thema    # hochladen
```

Danach auf GitHub einen **Pull Request** öffnen. Jemand anderes aus der
Gruppe schaut drüber und klickt auf **Merge**. So kennt jede Person den Code
der anderen, was für die mündliche Code-Prüfung wichtig ist.

## Datenquellen

- [FRED](https://fred.stlouisfed.org/series/DCOILBRENTEU): Brent (DCOILBRENTEU) und WTI (DCOILWTICO), Ursprung EIA
- Yahoo Finance über `yfinance`: Brent-Future (BZ=F), WTI-Future (CL=F)
- [Guardian Open Platform](https://open-platform.theguardian.com/): Artikel seit 1999
- [GDELT DOC 2.0 API](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) über `gdeltdoc`
- [Tagesschau-API](https://tagesschau.api.bund.dev/): max. 60 Abrufe pro Stunde, nur private, nicht-kommerzielle Nutzung

## Termine

- Abgabe Folien und Code: 28.01.2027, 23:59
- Vorträge: 29.01.2027
