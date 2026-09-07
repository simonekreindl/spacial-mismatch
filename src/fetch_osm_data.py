import requests
import time
import csv
import yaml
from datetime import date

# This script fetches point-of-interest data (e.g. shops, pharmacies) from
# OpenStreetMap for all categories defined in config.yaml, covering all of Slovenia.

# Source: OpenStreetMap contributors
# License: ODbL

# Load category definitions
with open("../config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

categories = config["categories"]

# Overpass API server this script sends queries to
url = "https://overpass-api.de/api/interpreter"

# Identifies this script to the server
headers = {
    "User-Agent": "SpatialMismatchResearch/1.0 (spacial-mismatch project, ZRC)"
}

def build_query(tags):
    # Builds an Overpass query for one category, searching both point (node)
    # and area (way) representations, since OSM stores places inconsistently.
    tag_filters = ""
    for tag in tags:
        key, value = tag.split("=")
        tag_filters += f'  node["{key}"="{value}"](area.si);\n'
        tag_filters += f'  way["{key}"="{value}"](area.si);\n'

    return f"""
    [out:json][timeout:120];
    area["ISO3166-1"="SI"][admin_level=2]->.si;
    (
    {tag_filters}
    );
    out center;
    """


def try_fetch(parent_cat, subcat, tags, max_retries=3, wait=15):
    # Attempts to fetch one category, retrying on connection errors or
    # server errors (timeouts, overload) up to max_retries times.
    query = build_query(tags)

    for attempt in range(max_retries):
        try:
            response = requests.post(url, data={"data": query}, headers=headers, timeout=150)
        except requests.exceptions.RequestException as e:
            print(f"{subcat}, attempt {attempt+1}: connection error ({e})")
            time.sleep(wait)
            continue

        if response.status_code == 200:
            data = response.json()
            elements = data["elements"]

            entries = []
            for el in elements:
                el_tags = el.get("tags", {})

                # Skip entries explicitly marked as no longer active
                if any(k.startswith("disused:") for k in el_tags.keys()):
                    continue

                # "way" results give a center point instead of lat/lon directly
                lat = el.get("lat") or el.get("center", {}).get("lat")
                lon = el.get("lon") or el.get("center", {}).get("lon")

                entries.append({
                    "osm_id": el.get("id"),
                    "osm_type": el.get("type"),
                    "name": el_tags.get("name", "unnamed"),
                    "category": subcat,
                    "parent_category": parent_cat,
                    "lat": lat,
                    "lon": lon,
                    "opening_hours": el_tags.get("opening_hours", ""),
                    "check_date": el_tags.get("check_date", ""),
                    "query_date": date.today().isoformat(),
                    "source": "OSM"
                })

            print(f"{subcat}: {len(elements)} results (whole Slovenia)")
            return entries
        else:
            print(f"{subcat}, attempt {attempt+1}: status {response.status_code}")
            time.sleep(wait)

    return None


all_results = []

# Flatten the nested category structure into a single list of tasks
pending = []
for parent_cat, subcats in categories.items():
    for subcat, tags in subcats.items():
        pending.append((parent_cat, subcat, tags))

# Run up to 3 full rounds: anything that fails gets retried in the next round,
# giving the server time to recover between attempts
for round_num in range(1, 4):
    if not pending:
        break
    print(f"\n--- Round {round_num}: {len(pending)} categories pending ---\n")
    still_pending = []

    for parent_cat, subcat, tags in pending:
        entries = try_fetch(parent_cat, subcat, tags)
        if entries is not None:
            all_results.extend(entries)
        else:
            still_pending.append((parent_cat, subcat, tags))
        time.sleep(2)  # avoid hammering the server between requests

    pending = still_pending

# Anything still pending after 3 rounds is a persistent failure
failed_permanently = pending

if all_results:
    with open("../data/raw/osm_raw_points.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\nDone! {len(all_results)} entries saved to osm_raw_points.csv")

if failed_permanently:
    # Written to a log file so gaps are visible and traceable
    print(f"\nWARNING: {len(failed_permanently)} categories failed permanently:")
    with open("../data/raw/failed_queries.log", "w", encoding="utf-8") as f:
        for parent_cat, subcat, tags in failed_permanently:
            line = f"{parent_cat}/{subcat}"
            print(f"  - {line}")
            f.write(line + "\n")
else:
    print("\nAll categories successful.")

