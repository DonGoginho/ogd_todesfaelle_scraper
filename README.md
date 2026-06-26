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

### Erweiterung Datenqualität

- **Duplikate**: Einzelne Personen erscheinen in mehreren Monats-Publikationen (identische Personendaten und identisches Sterbedatum, aber unterschiedlicher Todesmonat). Das CSV bildet die Quelle derzeit 1:1 ab — eine Deduplizierung ist noch nicht implementiert.

- **Grosse Abweichung zwischen Todesmonat und Sterbedatum**: Bei einem Teil der Einträge liegt der Todesmonat (= Publikationsmonat) deutlich nach dem Sterbedatum. Von rund 9500 Einträgen weisen 208 eine Differenz von mehr als 3 Monaten auf, 60 von mehr als 6 Monaten und 23 von mehr als einem Jahr. Beispiele:

  | Todesmonat | Name | Vorname | Sterbedatum | Differenz |
  |---|---|---|---|---|
  | 2024-07 | Walter | Theodore Eric | 2019-02-04 | ~5 Jahre |
  | 2023-07 | Hinrichsen | Aino | 2018-10-08 | ~5 Jahre |
  | 2024-03 | Leutert-Korga | Teresa-Julia | 2021-01-06 | ~3 Jahre |

  Mögliche Gründe sind verspätete Meldungen, Nachregistrierungen oder Todesfälle im Ausland, die erst später beim Bevölkerungsamt erfasst werden.

- **Vermutlicher Datenfehler**: Ein Eintrag (Todesmonat 2025-06, Sterbedatum 2005-04-03) weist eine Differenz von rund 20 Jahren auf. Dies ist mit hoher Wahrscheinlichkeit ein Erfassungsfehler in der Quelle.

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

## Datenquelle und technische Funktionsweise

Die Originaldaten werden vom Bevölkerungsamt der Stadt Zürich monatlich publiziert unter:

https://www.stadt-zuerich.ch/de/lebenslagen/tod/todesfaelle.html

Die Webseite rendert die Inhalte clientseitig per JavaScript. Der Scraper umgeht dies, indem er direkt die JSON-API des darunterliegenden **Adobe Experience Manager (AEM)** CMS anspricht. Die Daten werden in drei Schritten abgefragt:

1. **Jahre entdecken** — `https://www.stadt-zuerich.ch/de/lebenslagen/tod/todesfaelle.1.json` liefert alle verfügbaren Jahresseiten (z.B. 2023, 2024, 2025, 2026) als Kind-Knoten vom Typ `cq:Page`.

2. **Monate entdecken** — `.../{year}.1.json` liefert die verfügbaren Monatsseiten pro Jahr (z.B. `januar`, `februar`, `maerz`, ...). Die deutschen Monatsnamen sind Teil der URL-Struktur (`maerz` statt `märz`).

3. **Tabellendaten laden** — `.../{year}/{month}/_jcr_content/mainparsys.1.json` enthält die AEM-Komponenten der Seite. Die Todesfälle sind als HTML-Tabelle in der `tableData`-Property einer Tabellenkomponente gespeichert. Diese HTML-Tabelle wird mit BeautifulSoup geparst.

Beim inkrementellen Update (`python scrape.py` ohne `--full`) werden nur Monate geladen, die noch nicht in der bestehenden CSV enthalten sind.

## Lizenz

Die Quelldaten stehen unter der [Open Government Data Lizenz](https://www.stadt-zuerich.ch/de/politik-und-recht/amtliche-sammlung/ogd.html) der Stadt Zürich.
