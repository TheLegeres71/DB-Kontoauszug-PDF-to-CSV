# DB-Kontoauszug-PDF-to-CSV

**Python-Skript zur Extraktion von Deutschen Bank Kontoauszügen aus
PDF-Dateien und Export der Buchungen in CSV-Dateien.**

Dieses Tool automatisiert die Konvertierung von Kontoauszügen der
Deutschen Bank im PDF-Format in strukturierte CSV-Dateien. Jede
PDF-Datei wird analysiert und die enthaltenen Buchungen werden in eine
separate CSV-Datei exportiert.

---

## Features

- Automatische Verarbeitung mehrerer PDF-Kontoauszüge
- Extraktion von Buchungsdaten aus Deutsche Bank PDF-Kontoauszügen
- Erstellung einer CSV-Datei pro PDF-Datei
- Klar definierte CSV-Struktur
- Einfache und transparente Ordnerstruktur
- Keine externe Datenbank erforderlich
- Vollständig lokale Verarbeitung (keine Datenübertragung)
- Plattformunabhängig (Windows, macOS, Linux)

---

## Projektstruktur

```
DB-Kontoauszug-PDF-to-CSV/
│
├── pdf/                # Eingangsordner für Kontoauszüge im PDF-Format
├── csv/                # Ausgabeordner für generierte CSV-Dateien
├── CHANGELOG.md        # Änderungslog
├── main.py             # Python Skript zur Verarbeitung der PDF-Dateien
├── README.md           # Liesmich
└── requirements.txt    # Requirements 
```

---

## Voraussetzungen

### 1. Python

Erforderlich ist:

```
Python 3.9 oder neuer
```

Installierte Version prüfen:

```bash
python --version
```

oder:

```bash
python3 --version
```

Download unter:\
https://www.python.org/downloads/

**Wichtig unter Windows:**\
Während der Installation die Option aktivieren:

```
Add Python to PATH
```

---

### 2. Erforderliche Python Module

Das Skript verwendet folgende Module:

---

Modul Typ Beschreibung

---

pdfplumber extern Extraktion von Text und Buchungsdaten
 aus PDF-Dateien

csv Standardbibliothek Schreiben der CSV-Dateien

os Standardbibliothek Zugriff auf Dateisystem und Ordner

re Standardbibliothek Verarbeitung mittels regulärer
 Ausdrücke

---

Installation:

```bash
pip install pdfplumber
```

---

### 3. Virtuelle Umgebung (empfohlen)

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

```bash
pip install pdfplumber
```

---

## Verwendung

### Schritt 1: PDF-Dateien ablegen

Alle Deutsche Bank Kontoauszüge in den Ordner:

```
/pdf
```

### Schritt 2: Skript ausführen

```bash
python main.py
```

oder:

```bash
python3 main.py
```

### Schritt 3: Ergebnis

CSV-Dateien werden gespeichert in:

```
/csv
```

---

## CSV-Format

```
Buchungsdatum;Valutadatum;Buchungstext;Soll;Haben
```

---

## Funktionsweise

1. Durchsucht den Ordner `/pdf`
2. Öffnet PDF-Dateien mit pdfplumber
3. Extrahiert Buchungsdaten
4. Verarbeitet diese mit regulären Ausdrücken
5. Exportiert strukturierte CSV-Dateien
6. Speichert diese im Ordner `/csv`

---

## Zukünftige Features (geplant)

- Unterstützung weiterer Banken
- Unterstützung zusätzlicher PDF-Layouts
- Zusammenführung mehrerer PDFs
- CLI Argumente
- Logging
- Automatische Ordnererstellung

---

## Lizenz

GNU GENERAL PUBLIC LICENSE Version 3 (GPLv3)

https://www.gnu.org/licenses/gpl-3.0.html

---

## Autor

Andreas Friedrich