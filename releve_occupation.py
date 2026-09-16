import requests, csv, os, io
from datetime import datetime, timezone

CSV_URL = "https://www.data.gouv.fr/api/1/datasets/r/89185b1f-f958-4c5b-9282-399a66ecee97"

PDCS = [
    "FRLDLE00000839",
    "FRLDLE00000840",
]

# Chemin RELATIF cette fois : le script tourne dans le repo cloné par GitHub Actions
OUTPUT_FILE = "historique_occupation.csv"


def fetch_rows_for_pdcs():
    r = requests.get(CSV_URL, timeout=60)
    r.raise_for_status()
    reader = csv.DictReader(io.StringIO(r.text))
    rows = {}
    for row in reader:
        pdc_id = row.get("id_pdc_itinerance")
        if pdc_id in PDCS:
            rows[pdc_id] = row
    return rows


def get_last_horodatage(pdc_id):
    if not os.path.isfile(OUTPUT_FILE):
        return None
    last_value = None
    with open(OUTPUT_FILE, "r", newline="") as f:
        for row in csv.DictReader(f):
            if row["id_pdc_itinerance"] == pdc_id:
                last_value = row["horodatage"]
    return last_value


def main():
    file_exists = os.path.isfile(OUTPUT_FILE)
    rows = fetch_rows_for_pdcs()

    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["ts_releve_utc", "id_pdc_itinerance", "horodatage", "etat_pdc", "occupation_pdc"])

        for pdc in PDCS:
            row = rows.get(pdc)
            if row is None:
                print(f"[{pdc}] absent du fichier téléchargé")
                continue
            ts = row.get("horodatage")
            if ts != get_last_horodatage(pdc):
                ts_releve = datetime.now(timezone.utc).isoformat()
                writer.writerow([ts_releve, pdc, ts, row.get("etat_pdc"), row.get("occupation_pdc")])
                print(f"[{pdc}] changement -> {ts}")
            else:
                print(f"[{pdc}] pas de changement ({ts})")


if __name__ == "__main__":
    main()