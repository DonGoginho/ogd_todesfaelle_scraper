"""
Scraper für Todesfälle der Stadt Zürich.

Liest die Daten über die AEM JSON-API von stadt-zuerich.ch
und schreibt sie in ein OGD-konformes CSV.
"""

import argparse
import csv
import logging
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.stadt-zuerich.ch/de/lebenslagen/tod/todesfaelle"

MONTH_NAMES = [
    "januar", "februar", "maerz", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "dezember",
]

MONTH_NAME_TO_NUM = {name: i + 1 for i, name in enumerate(MONTH_NAMES)}

CSV_COLUMNS = [
    "Todesmonat",
    "Name",
    "Vorname",
    "Jahrgang",
    "Strasse",
    "Nummer",
    "PLZ",
    "Ort",
    "Sterbedatum",
]

OUTPUT_FILE = Path(__file__).parent / "data" / "todesfaelle_stadt_zuerich.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def discover_years() -> list[str]:
    data = fetch_json(f"{BASE_URL}.1.json")
    years = [
        key for key, val in data.items()
        if isinstance(val, dict) and val.get("jcr:primaryType") == "cq:Page" and re.fullmatch(r"\d{4}", key)
    ]
    return sorted(years)


def discover_months(year: str) -> list[str]:
    data = fetch_json(f"{BASE_URL}/{year}.1.json")
    months = [
        key for key, val in data.items()
        if isinstance(val, dict) and val.get("jcr:primaryType") == "cq:Page" and key in MONTH_NAME_TO_NUM
    ]
    return sorted(months, key=lambda m: MONTH_NAME_TO_NUM[m])


def fetch_table_html(year: str, month: str) -> str | None:
    url = f"{BASE_URL}/{year}/{month}/_jcr_content/mainparsys.1.json"
    data = fetch_json(url)
    for key, val in data.items():
        if isinstance(val, dict) and "tableData" in val:
            return val["tableData"]
    return None


def parse_table(html: str, year: str, month: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    if len(rows) < 2:
        return []

    month_num = MONTH_NAME_TO_NUM[month]
    todesmonat = f"{year}-{month_num:02d}"

    records = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue

        values = [c.get_text(strip=True) for c in cells]
        name, vorname, jahrgang, strasse, nummer, plz, ort, sterbedatum_raw = values[:8]

        sterbedatum = convert_date(sterbedatum_raw)

        records.append({
            "Todesmonat": todesmonat,
            "Name": name,
            "Vorname": vorname,
            "Jahrgang": jahrgang,
            "Strasse": strasse,
            "Nummer": nummer,
            "PLZ": plz,
            "Ort": ort,
            "Sterbedatum": sterbedatum,
        })

    return records


def convert_date(date_str: str) -> str:
    """DD.MM.YYYY -> YYYY-MM-DD"""
    match = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", date_str.strip())
    if match:
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return date_str


def load_existing_months(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {row["Todesmonat"] for row in reader}


def write_csv(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper für Todesfälle Stadt Zürich")
    parser.add_argument("--full", action="store_true", help="Alle Daten neu laden (kein inkrementelles Update)")
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE, help="Pfad zur CSV-Ausgabedatei")
    args = parser.parse_args()

    output = args.output

    existing_records = []
    existing_months = set()

    if not args.full and output.exists():
        with open(output, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            existing_records = list(reader)
        existing_months = {r["Todesmonat"] for r in existing_records}
        log.info("Bestehende CSV mit %d Einträgen geladen (%d Monate)", len(existing_records), len(existing_months))

    years = discover_years()
    log.info("Verfügbare Jahre: %s", ", ".join(years))

    new_records = []

    for year in years:
        months = discover_months(year)
        log.info("Jahr %s: %d Monate verfügbar", year, len(months))

        for month in months:
            month_num = MONTH_NAME_TO_NUM[month]
            todesmonat = f"{year}-{month_num:02d}"

            if todesmonat in existing_months:
                log.info("  %s bereits vorhanden, überspringe", todesmonat)
                continue

            log.info("  Lade %s/%s ...", year, month)
            html = fetch_table_html(year, month)
            if not html:
                log.warning("  Keine Tabellendaten für %s/%s", year, month)
                continue

            records = parse_table(html, year, month)
            log.info("  %d Einträge gefunden", len(records))
            new_records.extend(records)

    all_records = existing_records + new_records
    all_records.sort(key=lambda r: (r["Todesmonat"], r["Name"], r["Vorname"]))

    write_csv(all_records, output)
    log.info("CSV geschrieben: %s (%d Einträge total, %d neu)", output, len(all_records), len(new_records))


if __name__ == "__main__":
    main()
