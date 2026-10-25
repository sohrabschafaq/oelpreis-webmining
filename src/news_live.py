"""Schritt 2b: Aktuelle Nachrichten täglich sammeln (GDELT und Tagesschau).

Dieses Skript wird ab Ende November einmal pro Tag gestartet. Jeder Lauf
speichert die Meldungen des Tages als eigene Datei, so wachsen die Daten
bis Januar von allein.

Start:   python src/news_live.py
Ergebnis: data/raw/gdelt/<datum>_*.csv und data/raw/tagesschau/<datum>.json

Regeln:
- Tagesschau: höchstens 60 Abrufe pro Stunde, nur private und
  nicht-kommerzielle Nutzung, Texte nicht veröffentlichen.
- GDELT: offiziell nur die letzten 3 Monate abrufbar, deshalb täglich sammeln.
"""

import json
import time
from datetime import date, timedelta

import requests
from gdeltdoc import Filters, GdeltDoc

from config import CRISIS_KEYWORDS_DE, CRISIS_KEYWORDS_EN, RAW_DIR

TAGESSCHAU_URL = "https://www.tagesschau.de/api2u/search/"
PAUSE_SECONDS = 2.0  # 60 Abrufe pro Stunde wären eine Minute Pause; wir machen nur wenige


def collect_gdelt(today: date) -> None:
    """Artikelliste sowie Menge und Ton pro Tag für die letzten 7 Tage."""
    out_dir = RAW_DIR / "gdelt"
    out_dir.mkdir(exist_ok=True)
    filters = Filters(
        keyword=CRISIS_KEYWORDS_EN,
        start_date=(today - timedelta(days=7)).isoformat(),
        end_date=today.isoformat(),
    )
    gd = GdeltDoc()
    gd.article_search(filters).to_csv(out_dir / f"{today}_articles.csv", index=False)
    gd.timeline_search("timelinevol", filters).to_csv(out_dir / f"{today}_volume.csv", index=False)
    gd.timeline_search("timelinetone", filters).to_csv(out_dir / f"{today}_tone.csv", index=False)
    print("GDELT gespeichert.")


def collect_tagesschau(today: date) -> None:
    """Sucht jeden deutschen Suchbegriff einmal und speichert die Rohantworten."""
    out_dir = RAW_DIR / "tagesschau"
    out_dir.mkdir(exist_ok=True)
    results = {}
    for keyword in CRISIS_KEYWORDS_DE:
        params = {"searchText": keyword, "pageSize": 30}
        response = requests.get(TAGESSCHAU_URL, params=params, timeout=30)
        response.raise_for_status()
        results[keyword] = response.json()
        time.sleep(PAUSE_SECONDS)
    out_file = out_dir / f"{today}.json"
    out_file.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
    print(f"Tagesschau gespeichert ({len(CRISIS_KEYWORDS_DE)} Abrufe).")


def main() -> None:
    today = date.today()
    collect_gdelt(today)
    collect_tagesschau(today)
    # TODO: täglich automatisch starten, z.B. mit der Windows-Aufgabenplanung
    # oder einer GitHub Action (dann aber Rohdaten nicht ins öffentliche Repo).


if __name__ == "__main__":
    main()
