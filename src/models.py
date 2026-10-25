"""Schritt 5: Modelle vergleichen (Kern der Forschungsfrage).

Vergleicht Prognosen nur mit Preisdaten gegen Prognosen mit zusätzlichen
Nachrichten-Features. Training bis TRAIN_END, Test danach. Fehlermaß ist
der mittlere absolute Fehler (MAE): kleiner ist besser.

Start:   python src/models.py
Ergebnis: data/processed/model_results.csv und data/processed/predictions.csv
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from config import PROCESSED_DIR, TRAIN_END

PRICE_FEATURES = ["return_lag1", "return_lag2", "return_lag3", "return_lag5", "volatility_5d"]
NEWS_FEATURES = [
    "n_articles",
    "n_articles_3d",
    "n_articles_7d",
    "sentiment",
    "sentiment_3d",
    "sentiment_7d",
]


def main() -> None:
    df = pd.read_csv(PROCESSED_DIR / "features.csv", parse_dates=["date"], index_col="date")
    # Tage ohne Nachrichten haben keine Stimmung: neutral (0) annehmen.
    df[NEWS_FEATURES] = df[NEWS_FEATURES].fillna(0)

    train = df[df.index <= TRAIN_END]
    test = df[df.index > TRAIN_END]
    print(f"Training: {len(train)} Tage, Test: {len(test)} Tage")

    predictions = pd.DataFrame({"target": test["target"]})

    # Baseline "morgen wie heute": keine Änderung erwartet.
    predictions["baseline"] = 0.0

    models = {
        "linreg_preise": (LinearRegression(), PRICE_FEATURES),
        "rf_preise": (RandomForestRegressor(n_estimators=300, random_state=42), PRICE_FEATURES),
        "rf_preise_nachrichten": (
            RandomForestRegressor(n_estimators=300, random_state=42),
            PRICE_FEATURES + NEWS_FEATURES,
        ),
    }
    for name, (model, features) in models.items():
        model.fit(train[features], train["target"])
        predictions[name] = model.predict(test[features])

    results = pd.DataFrame(
        {
            "modell": [c for c in predictions.columns if c != "target"],
            "mae": [
                mean_absolute_error(predictions["target"], predictions[c])
                for c in predictions.columns
                if c != "target"
            ],
        }
    ).sort_values("mae")

    # Wichtigkeit der Features im Modell mit Nachrichten (für den Vortrag).
    rf_news, news_cols = models["rf_preise_nachrichten"]
    importance = pd.Series(rf_news.feature_importances_, index=news_cols).sort_values()
    importance.to_csv(PROCESSED_DIR / "feature_importance.csv", header=["importance"])

    predictions.to_csv(PROCESSED_DIR / "predictions.csv")
    results.to_csv(PROCESSED_DIR / "model_results.csv", index=False)
    print(results.to_string(index=False))
    # TODO (Gruppe): weitere Ziele testen (z.B. 5 Tage, Schwankung statt Preisänderung).


if __name__ == "__main__":
    main()
