"""Schritt 1: Preisdaten holen.

Lädt die täglichen Brent- und WTI-Preise von FRED (Hauptquelle) und
Yahoo Finance (Kontrolle), speichert die Rohdaten und vergleicht beide.

Start:   python src/prices.py
Ergebnis: data/processed/prices.csv (eine Zeile pro Handelstag)
"""

import pandas as pd
import yfinance as yf

from config import PROCESSED_DIR, RAW_DIR, START_DATE

# FRED-Serien: Spotpreise in US-Dollar pro Barrel, Ursprung EIA.
FRED_SERIES = {"brent": "DCOILBRENTEU", "wti": "DCOILWTICO"}
# Yahoo-Ticker: Future-Preise, also ein etwas anderes Produkt als der Spotpreis.
YAHOO_TICKERS = {"brent": "BZ=F", "wti": "CL=F"}

# Ab wie viel Prozent Unterschied wir einen Tag als auffällig markieren.
MAX_DIFF_PERCENT = 5.0


def load_fred(series_id: str) -> pd.Series:
    """Lädt eine FRED-Serie als CSV, ganz ohne API-Schlüssel."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    # FRED schreibt fehlende Werte als "." – das machen wir zu NaN.
    df = pd.read_csv(url, na_values=".")
    df.to_csv(RAW_DIR / f"fred_{series_id}.csv", index=False)
    date_col = df.columns[0]  # heißt je nach Version "DATE" oder "observation_date"
    df[date_col] = pd.to_datetime(df[date_col])
    return df.set_index(date_col)[series_id]


def load_yahoo(ticker: str) -> pd.Series:
    """Lädt die Schlusskurse eines Tickers von Yahoo Finance."""
    df = yf.download(ticker, start=START_DATE, progress=False, auto_adjust=False)
    df.to_csv(RAW_DIR / f"yahoo_{ticker.replace('=', '_')}.csv")
    close = df["Close"]
    # Neuere yfinance-Versionen liefern eine Tabelle statt einer Spalte.
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return close


def main() -> None:
    columns = {}
    for name, series_id in FRED_SERIES.items():
        print(f"Lade FRED {series_id} ...")
        columns[f"{name}_fred"] = load_fred(series_id)
    for name, ticker in YAHOO_TICKERS.items():
        print(f"Lade Yahoo {ticker} ...")
        columns[f"{name}_yahoo"] = load_yahoo(ticker)

    prices = pd.DataFrame(columns)
    prices = prices[prices.index >= START_DATE]
    prices.index.name = "date"

    # Abgleich: Wie stark weicht Yahoo von FRED ab?
    for name in FRED_SERIES:
        fred, yahoo = prices[f"{name}_fred"], prices[f"{name}_yahoo"]
        prices[f"{name}_diff_pct"] = (yahoo - fred) / fred * 100
        prices[f"{name}_check"] = (
            prices[f"{name}_diff_pct"].abs() > MAX_DIFF_PERCENT
        ) | fred.isna() | yahoo.isna()

    # Nur Tage behalten, an denen FRED einen Brent-Preis hat (Hauptquelle).
    prices = prices.dropna(subset=["brent_fred"])
    prices.to_csv(PROCESSED_DIR / "prices.csv")

    print(f"Gespeichert: {len(prices)} Handelstage in data/processed/prices.csv")
    for name in FRED_SERIES:
        print(f"  {name}: {prices[f'{name}_check'].sum()} Tage zum Prüfen markiert")


if __name__ == "__main__":
    main()
