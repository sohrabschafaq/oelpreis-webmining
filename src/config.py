"""Gemeinsame Einstellungen für alle Skripte.

Alles, was mehrere Schritte brauchen (Ordner, Zeitraum, Suchbegriffe,
API-Schlüssel), steht hier an einer Stelle. Wer etwas ändern will,
ändert es nur hier.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# --- Ordner -------------------------------------------------------------
# ROOT ist der Hauptordner des Repos, egal von wo das Skript gestartet wird.
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"

for folder in (RAW_DIR, PROCESSED_DIR, FIGURES_DIR):
    folder.mkdir(parents=True, exist_ok=True)

# --- API-Schlüssel aus der Datei .env -----------------------------------
load_dotenv(ROOT / ".env")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
EIA_API_KEY = os.getenv("EIA_API_KEY", "")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY", "")

# --- Zeitraum -----------------------------------------------------------
START_DATE = "2015-01-01"
# Alles bis hier ist Trainingsdaten, alles danach Testdaten (Schritt 5).
TRAIN_END = "2023-12-31"

# --- Krisen-Suchbegriffe ------------------------------------------------
# TODO (Gruppe): Liste gemeinsam festlegen und im Vortrag begründen.
CRISIS_KEYWORDS_EN = [
    "oil",
    "OPEC",
    "sanctions",
    "Iran",
    "Russia",
    "Red Sea",
    "Strait of Hormuz",
    "pipeline attack",
]
CRISIS_KEYWORDS_DE = [
    "Öl",
    "OPEC",
    "Sanktionen",
    "Iran",
    "Russland",
    "Rotes Meer",
    "Straße von Hormus",
]
