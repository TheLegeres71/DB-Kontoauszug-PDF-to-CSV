"""
DB-Kontoauszug-PDF-to-CSV
Version: 0.1.0
Autor: Andreas Friedrich
Lizenz: GNU General Public License v3.0 (GPL-3.0)
Datum: 2026-02-19

Beschreibung:
Dieses Skript extrahiert Buchungsdaten aus PDF-Kontoauszügen der Deutschen Bank
und exportiert diese in strukturierte CSV-Dateien.

Funktionsweise:
- Liest alle PDF-Dateien aus dem Verzeichnis /pdf
- Extrahiert Buchungsdatum, Valutadatum, Buchungstext sowie Soll/Haben-Beträge
- Erkennt mehrzeilige Buchungstexte
- Exportiert jede PDF-Datei als separate CSV-Datei in das Verzeichnis /csv

CSV-Format:
Buchungsdatum;Valutadatum;Buchungstext;Soll;Haben

Abhängigkeiten:
- pdfplumber
- csv (Standardbibliothek)
- os (Standardbibliothek)
- re (Standardbibliothek)
"""

import pdfplumber
import csv
import os
import re

# Eingabe- und Ausgabe-Verzeichnisse
INPUT_DIR = "pdf"
OUTPUT_DIR = "csv"

# Sicherstellen, dass das Ausgabe-Verzeichnis existiert
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regulärer Ausdruck zur Erkennung eines Datums im Format TT.MM.
DATE_PATTERN = re.compile(r"^\d{2}\.\d{2}\.$")

# Regulärer Ausdruck zur Erkennung eines Betrags im deutschen Format (z.B. -1.234,56)
AMOUNT_PATTERN = re.compile(r"[-+]?\d{1,3}(?:\.\d{3})*,\d{2}")


def group_rows(words, tolerance=2):
    """
    Gruppiert extrahierte PDF-Wörter zu logischen Zeilen basierend auf ihrer vertikalen Position.

    pdfplumber liefert einzelne Wörter mit Positionsinformationen. Diese Funktion fasst
    Wörter zusammen, die sich auf ähnlicher Y-Position befinden, um vollständige Tabellenzeilen
    zu rekonstruieren.

    Parameter:
        words (list): Liste von Wort-Dictionaries aus pdfplumber.extract_words()
        tolerance (int): Toleranzbereich für vertikale Gruppierung

    Returns:
        list: Liste von Zeilen, wobei jede Zeile eine Liste von Wort-Dictionaries enthält
    """

    rows = {}

    for w in words:
        # Gruppierung anhand der vertikalen Position ("top")
        key = round(w["top"] / tolerance) * tolerance
        rows.setdefault(key, []).append(w)

    result = []

    for k in sorted(rows.keys()):
        # Sortierung der Wörter innerhalb einer Zeile nach horizontaler Position
        row = sorted(rows[k], key=lambda x: x["x0"])
        result.append(row)

    return result


def clean_booking_text(text, booking_date, value_date):
    """
    Bereinigt den Buchungstext durch Entfernen redundanter oder irrelevanter Inhalte.

    Entfernt:
    - Buchungsdatum und Valutadatum
    - Jahreszahlen (z.B. 2025)
    - Technische Referenznummern
    - Mehrfache Leerzeichen

    Parameter:
        text (str): Originaltext
        booking_date (str): Buchungsdatum
        value_date (str): Valutadatum

    Returns:
        str: Bereinigter Buchungstext
    """

    text = text.replace(booking_date, "")
    text = text.replace(value_date, "")

    # Entferne isolierte Jahreszahlen
    text = re.sub(r"\b2025\b", "", text)

    # Entferne lange technische Referenznummern
    text = re.sub(r"2020\d{10,}", "", text)

    # Normalisiere Leerzeichen
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_transactions(pdf_path):
    """
    Extrahiert alle Buchungstransaktionen aus einem Deutsche Bank PDF-Kontoauszug.

    Erkennt:
    - Buchungsdatum
    - Valutadatum
    - Buchungstext (auch mehrzeilig)
    - Soll-Beträge
    - Haben-Beträge

    Parameter:
        pdf_path (str): Pfad zur PDF-Datei

    Returns:
        list: Liste von Transaktionen im Format:
              [Buchungsdatum, Valutadatum, Buchungstext, Soll, Haben]
    """

    transactions = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            # Extrahiere Wörter mit Positionsinformationen
            words = page.extract_words()

            # Gruppiere Wörter zu Zeilen
            rows = group_rows(words)

            current = None

            for row in rows:

                texts = [w["text"] for w in row]

                # Überspringe Header- und Footer-Bereiche
                if "Auszug" in texts or ("IBAN" in texts and "Buchung" in texts):
                    continue

                booking_date = None
                value_date = None

                # Erkenne Buchungsdatum und Valutadatum
                if len(texts) >= 2 and DATE_PATTERN.match(texts[0]) and DATE_PATTERN.match(texts[1]):
                    booking_date = texts[0]
                    value_date = texts[1]

                amount = None

                # Suche nach Betrag innerhalb der Zeile
                for t in texts:
                    if AMOUNT_PATTERN.match(t):
                        amount = t
                        break

                is_transaction_start = booking_date and amount

                if is_transaction_start:

                    # Vorherige Transaktion abschließen
                    if current:
                        transactions.append(current)

                    soll = ""
                    haben = ""

                    # Negative Beträge = Soll (Debit)
                    if "-" in amount:
                        soll = amount.replace("-", "")
                    else:
                        # Positive Beträge = Haben (Credit)
                        haben = amount.replace("+", "")

                    # Extrahiere Buchungstext
                    booking_text = " ".join(texts[2:])

                    booking_text = clean_booking_text(
                        booking_text,
                        booking_date,
                        value_date
                    )

                    current = [
                        booking_date,
                        value_date,
                        booking_text,
                        soll,
                        haben
                    ]

                elif current:
                    # Mehrzeilige Buchung fortsetzen
                    continuation = clean_booking_text(
                        " ".join(texts),
                        "",
                        ""
                    )

                    current[2] += " " + continuation

            # Letzte Transaktion hinzufügen
            if current:
                transactions.append(current)

    return transactions


def main():
    """
    Hauptfunktion des Skripts.

    Ablauf:
    - Durchsucht das INPUT_DIR nach PDF-Dateien
    - Extrahiert Transaktionen aus jeder PDF-Datei
    - Schreibt Ergebnisse in CSV-Dateien im OUTPUT_DIR
    """

    for file in os.listdir(INPUT_DIR):

        # Nur PDF-Dateien verarbeiten
        if not file.endswith(".pdf"):
            continue

        path = os.path.join(INPUT_DIR, file)

        # Transaktionen extrahieren
        transactions = extract_transactions(path)

        # Zielpfad für CSV-Datei
        out = os.path.join(
            OUTPUT_DIR,
            file.replace(".pdf", ".csv")
        )

        # CSV-Datei schreiben
        with open(out, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f, delimiter=";")

            # Header schreiben
            writer.writerow([
                "Buchungsdatum",
                "Valutadatum",
                "Buchungstext",
                "Soll",
                "Haben"
            ])

            # Transaktionen schreiben
            writer.writerows(transactions)

        print("Fertig:", out)


if __name__ == "__main__":
    main()
