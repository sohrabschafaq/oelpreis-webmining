"""Schritt 4: Features pro Tag bauen.

Führt Preise (Schritt 1) und Nachrichten (Schritt 3) pro Tag zusammen.

Wichtig gegen "Blick in die Zukunft": Nachrichten von Tag X dürfen nur
für die Prognose von Tag X+1 benutzt werden. Deshalb verschieben wir
alle Nachrichten-Features um einen Tag (shift(1)).

Start:   python src/features.py
Ergebnis: data/processed/features.csv (eine Zeile pro Handelstag)
"""

import pandas as pd

from config import PROCESSED_DIR

# Was wir vorhersagen: Preisänderung in Prozent über die nächsten N Handelstage.
HORIZON_DAYS = 1


def main() -> None:
    prices = pd.read_csv(PROCESSED_DIR / "prices.csv", parse_dates=["date"], index_col="date")
    articles = pd.read_csv(PROCESSED_DIR / "articles.csv", parse_dates=["date"])

    # Nachrichten pro Kalendertag: Anzahl und durchschnittliche Stimmung.
    news = articles.groupby("date").agg(
        n_articles=("id", "count"), sentiment=("sentiment", "mean")
    )
    # Auf alle Kalendertage auffüllen, damit Wochenend-Nachrichten nicht verloren gehen.
    news = news.asfreq("D").fillna({"n_articles": 0})
    news["n_articles_3d"] = news["n_articles"].rolling(3).mean()
    news["n_articles_7d"] = news["n_articles"].rolling(7).mean()
    news["sentiment_3d"] = news["sentiment"].rolling(3, min_periods=1).mean()
    news["sentiment_7d"] = news["sentiment"].rolling(7, min_periods=1).mean()
    news = news.shift(1)  # Nachrichten von gestern für heute

    df = pd.DataFrame(index=prices.index)
    df["brent"] = prices["brent_fred"]
    df["return_1d"] = df["brent"].pct_change() * 100
    for lag in (1, 2, 3, 5):
        df[f"return_lag{lag}"] = df["return_1d"].shift(lag - 1)
    df["volatility_5d"] = df["return_1d"].rolling(5).std()

    df = df.join(news, how="left")

    # Ziel: Änderung bis HORIZON_DAYS Handelstage in der Zukunft.
    df["target"] = (df["brent"].shift(-HORIZON_DAYS) / df["brent"] - 1) * 100

    df = df.dropna(subset=["target", "return_lag5", "volatility_5d"])
    df.to_csv(PROCESSED_DIR / "features.csv")
    print(f"Gespeichert: {len(df)} Tage in data/processed/features.csv")


if __name__ == "__main__":
    main()
