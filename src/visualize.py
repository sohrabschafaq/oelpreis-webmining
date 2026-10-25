"""Schritt 6: Ergebnisse zeigen.

Erstellt die Abbildungen für den Vortrag aus den Dateien der Schritte 1–5.

Start:   python src/visualize.py
Ergebnis: PNG-Dateien in reports/figures/
"""

import matplotlib.pyplot as plt
import pandas as pd

from config import FIGURES_DIR, PROCESSED_DIR


def plot_prices_with_news() -> None:
    """Brent-Preis und Menge der Krisenartikel übereinander."""
    df = pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["date"], index_col="date")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    ax1.plot(df.index, df["brent"])
    ax1.set_ylabel("Brent (USD/Barrel)")
    ax1.set_title("Ölpreis und Krisennachrichten")
    ax2.plot(df.index, df["n_articles_7d"], color="tab:red")
    ax2.set_ylabel("Krisenartikel (7-Tage-Mittel)")
    # TODO: wichtige Krisen markieren, z.B. ax1.axvline(pd.Timestamp("2022-02-24"))
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "preis_und_nachrichten.png", dpi=150)


def plot_model_errors() -> None:
    """Balkendiagramm: Fehler (MAE) jedes Modells."""
    results = pd.read_csv(PROCESSED_DIR / "model_results.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(results["modell"], results["mae"])
    ax.set_xlabel("Mittlerer absoluter Fehler (Prozentpunkte), kleiner ist besser")
    ax.set_title("Modellvergleich im Testzeitraum")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "modellvergleich.png", dpi=150)


def plot_feature_importance() -> None:
    importance = pd.read_csv(PROCESSED_DIR / "feature_importance.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(importance.index, importance["importance"])
    ax.set_title("Wichtigkeit der Features (Random Forest mit Nachrichten)")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "feature_wichtigkeit.png", dpi=150)


def main() -> None:
    plot_prices_with_news()
    plot_model_errors()
    plot_feature_importance()
    print("Abbildungen gespeichert in reports/figures/")
    # Optional: Streamlit-Dashboard mit aktuellem Preis, Krisen-Index und Prognose.


if __name__ == "__main__":
    main()
