"""Schritt 2a: Nachrichten-Archiv vom Guardian laden.

Holt alle Artikel zu unseren Krisen-Suchbegriffen ab START_DATE über die
Guardian Content API. Braucht einen kostenlosen Schlüssel in der .env.

Start:   python src/news_guardian.py
Ergebnis: data/raw/guardian/<jahr>.json (Rohdaten, eine Datei pro Jahr)

Hinweis: Der kostenlose Schlüssel erlaubt etwa 500 Abrufe pro Tag.
Wenn das Limit erreicht ist, einfach morgen weitermachen: Jahre, die schon
gespeichert sind, werden übersprungen.
"""

import json
import time
from datetime import date

import requests

from config import CRISIS_KEYWORDS_EN, GUARDIAN_API_KEY, RAW_DIR, START_DATE

API_URL = "https://content.guardianapis.com/search"
OUT_DIR = RAW_DIR / "guardian"
PAUSE_SECONDS = 1.0  # Pause zwischen zwei Abrufen, um die API zu schonen


def build_query() -> str:
    """Verbindet die Suchbegriffe mit OR, Begriffe mit Leerzeichen in Anführungszeichen."""
    terms = [f'"{k}"' if " " in k else k for k in CRISIS_KEYWORDS_EN]
    return " OR ".join(terms)


def fetch_year(year: int) -> list[dict]:
    """Lädt alle Seiten der Suchergebnisse für ein Jahr."""
    articles, page, pages = [], 1, 1
    while page <= pages:
        params = {
            "q": build_query(),
            "from-date": f"{year}-01-01",
            "to-date": f"{year}-12-31",
            "page-size": 200,  # Maximum der API
            "page": page,
            "show-fields": "headline,trailText,bodyText",
            "api-key": GUARDIAN_API_KEY,
        }
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()["response"]
        articles.extend(data["results"])
        pages = data["pages"]
        print(f"  {year}: Seite {page}/{pages}")
        page += 1
        time.sleep(PAUSE_SECONDS)
    return articles


def main() -> None:
    if not GUARDIAN_API_KEY:
        raise SystemExit("Kein GUARDIAN_API_KEY in der .env gefunden (siehe .env.example).")
    OUT_DIR.mkdir(exist_ok=True)

    # TODO (Gruppe): Die Suche ist breit ("oil" allein liefert sehr viel).
    # Nach dem ersten Test prüfen, ob wir die Abfrage enger fassen.
    for year in range(int(START_DATE[:4]), date.today().year + 1):
        out_file = OUT_DIR / f"{year}.json"
        if out_file.exists():
            print(f"{year} schon vorhanden, übersprungen.")
            continue
        print(f"Lade {year} ...")
        articles = fetch_year(year)
        out_file.write_text(json.dumps(articles, ensure_ascii=False), encoding="utf-8")
        print(f"  {len(articles)} Artikel gespeichert.")


if __name__ == "__main__":
    main()
