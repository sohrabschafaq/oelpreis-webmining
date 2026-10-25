"""Schritt 3: Texte aufbereiten und Stimmung (Sentiment) bestimmen.

Liest die Rohdaten aus Schritt 2, entfernt Duplikate, bereinigt die Texte,
tokenisiert sie mit NLTK und gibt jedem Artikel einen Stimmungswert
zwischen -1 (sehr negativ) und +1 (sehr positiv).

Start:   python src/text_prep.py
Ergebnis: data/processed/articles.csv (eine Zeile pro Artikel)
"""

import json
import re

import nltk
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer

from config import PROCESSED_DIR, RAW_DIR

# "vader" ist schnell und braucht nichts außer NLTK, versteht aber nur Englisch.
# "ollama" fragt ein lokales Sprachmodell (vorher Ollama installieren).
SENTIMENT_METHOD = "vader"
OLLAMA_MODEL = "llama3.2"


def load_guardian() -> pd.DataFrame:
    """Alle Guardian-Jahresdateien zu einer Tabelle zusammenführen."""
    rows = []
    for file in sorted((RAW_DIR / "guardian").glob("*.json")):
        for article in json.loads(file.read_text(encoding="utf-8")):
            fields = article.get("fields", {})
            rows.append(
                {
                    "source": "guardian",
                    "id": article["id"],
                    "date": article["webPublicationDate"][:10],
                    "title": fields.get("headline", article.get("webTitle", "")),
                    "text": fields.get("bodyText", ""),
                }
            )
    return pd.DataFrame(rows)


# TODO: load_gdelt(), load_tagesschau() und load_crawler() ergänzen,
# sobald die ersten Rohdaten aus news_live.py und news_crawler.py da sind.


def clean_text(text: str) -> str:
    """Kleinbuchstaben, nur Buchstaben und Ziffern, einfache Leerzeichen."""
    text = text.lower()
    text = re.sub(r"[^a-zäöüß0-9 ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sentiment_vader(analyzer: SentimentIntensityAnalyzer, text: str) -> float:
    return analyzer.polarity_scores(text)["compound"]


def sentiment_ollama(text: str) -> float:
    """Fragt ein lokales LLM nach einer Zahl von -1 bis 1."""
    import ollama

    prompt = (
        "Bewerte die Stimmung dieses Nachrichtentextes für den Ölmarkt "
        "mit einer einzigen Zahl von -1 (sehr negativ) bis 1 (sehr positiv). "
        "Antworte nur mit der Zahl.\n\n" + text[:2000]
    )
    answer = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)["response"]
    match = re.search(r"-?\d+(\.\d+)?", answer)
    return float(match.group()) if match else 0.0


def main() -> None:
    nltk.download("punkt_tab", quiet=True)
    nltk.download("vader_lexicon", quiet=True)

    articles = load_guardian()
    if articles.empty:
        raise SystemExit("Keine Rohdaten gefunden. Zuerst src/news_guardian.py starten.")

    articles = articles.drop_duplicates(subset=["source", "id"])
    articles = articles.drop_duplicates(subset=["title", "date"])
    articles["clean"] = articles["text"].fillna("").map(clean_text)
    articles["n_tokens"] = articles["clean"].map(lambda t: len(nltk.word_tokenize(t)))

    # Für das Sentiment reichen Überschrift und Textanfang.
    short = articles["title"].fillna("") + ". " + articles["text"].fillna("").str[:500]
    if SENTIMENT_METHOD == "ollama":
        articles["sentiment"] = short.map(sentiment_ollama)
    else:
        analyzer = SentimentIntensityAnalyzer()
        articles["sentiment"] = short.map(lambda t: sentiment_vader(analyzer, t))

    # Volltexte nicht mitspeichern, nur was die nächsten Schritte brauchen.
    out = articles[["source", "id", "date", "title", "n_tokens", "sentiment"]]
    out.to_csv(PROCESSED_DIR / "articles.csv", index=False)
    print(f"Gespeichert: {len(out)} Artikel in data/processed/articles.csv")


if __name__ == "__main__":
    main()
