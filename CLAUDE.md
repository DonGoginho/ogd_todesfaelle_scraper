# Todesfälle Stadt Zürich - Scraper

## Projektübersicht
Scraper für die publizierten Todesfälle der Stadt Zürich. Liest Daten über die AEM JSON-API von stadt-zuerich.ch und schreibt sie in ein OGD-konformes CSV.

## Architektur
- **Datenquelle**: AEM JSON-API (kein JS-Rendering nötig)
  - Jahre: `https://www.stadt-zuerich.ch/de/lebenslagen/tod/todesfaelle.1.json`
  - Monate: `.../{year}.1.json`
  - Tabellendaten: `.../{year}/{month}/_jcr_content/mainparsys.1.json` → `tableData`-Property
- **Parsing**: BeautifulSoup parst die HTML-Tabelle aus der `tableData`-Property
- **Output**: `data/todesfaelle_stadt_zuerich.csv` (UTF-8, Komma-separiert)

## Befehle
```bash
pip install -r requirements.txt    # Dependencies installieren
python scrape.py                   # Inkrementelles Update (nur neue Monate)
python scrape.py --full            # Alle Daten neu laden
python scrape.py --output pfad.csv # Alternativer Output-Pfad
```

## Automatisierung
GitHub Actions Workflow (`.github/workflows/scrape.yml`) läuft am 8. jedes Monats. Manuell auslösbar via `workflow_dispatch`.

## Konventionen
- Python 3.12+
- Keine zusätzlichen Dependencies ohne guten Grund
- CSV-Datumsformate: Sterbedatum als `YYYY-MM-DD`, Todesmonat als `YYYY-MM`
- Deutsche Monatsnamen in URLs: `maerz` (nicht `märz`)
