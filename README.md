# Todesfälle Stadt Zürich

Scraper für die auf [stadt-zuerich.ch](https://www.stadt-zuerich.ch/de/lebenslagen/tod/todesfaelle.html) publizierten Todesfälle von Stadtzürcher Einwohner\*innen.

## Daten

Die CSV-Datei `data/todesfaelle_stadt_zuerich.csv` enthält folgende Felder:

| Feld | Beschreibung | Format |
|------|-------------|--------|
| Todesmonat | Monat der Meldung beim Bevölkerungsamt | `YYYY-MM` |
| Name | Nachname | Text |
| Vorname | Vorname(n) | Text |
| Jahrgang | Geburtsjahr | `YYYY` |
| Strasse | Strasse des letzten Wohnsitzes | Text |
| Nummer | Hausnummer | Text |
| PLZ | Postleitzahl | Text |
| Ort | Wohnort | Text |
| Sterbedatum | Todesdatum | `YYYY-MM-DD` |

Verfügbare Daten: ab 2023 (abhängig von der Publikation durch das Bevölkerungsamt).

**Format**: UTF-8, Komma-separiert (RFC 4180).

## Nutzung

### Erstmaliger Lauf (alle Daten laden)

```bash
pip install -r requirements.txt
python scrape.py --full
```

### Monatliches Update (nur neue Monate)

```bash
python scrape.py
```

### Automatisierung via GitHub Actions

Der Workflow `.github/workflows/scrape.yml` läuft am 8. jedes Monats automatisch und committed neue Daten ins Repository. Er kann auch manuell über die GitHub-Oberfläche gestartet werden (Actions > "Todesfälle scrapen" > "Run workflow").

## Datenquelle

Die Daten werden über die AEM JSON-API von stadt-zuerich.ch bezogen. Die Originaldaten werden vom Bevölkerungsamt der Stadt Zürich monatlich publiziert unter:

https://www.stadt-zuerich.ch/de/lebenslagen/tod/todesfaelle.html

## Lizenz

Die Quelldaten stehen unter der [Open Government Data Lizenz](https://www.stadt-zuerich.ch/de/politik-und-recht/amtliche-sammlung/ogd.html) der Stadt Zürich.
