# Spatial Mismatch Slovenia

This code builds a database of services (shops, doctors, schools, and more) and population numbers for all 212 Slovenian municipalities. Everything is collected, cleaned, and matched to the right municipality automatically. As a first, simple use of that data, it also calculates a mismatch score per category, showing which municipalities have notably more or fewer services than their population would suggest.

It does this in six steps:

1. Downloads the official boundaries of all 212 Slovenian municipalities
2. Downloads the locations of shops, doctors, schools, etc. from OpenStreetMap, based on categories defined in `config.yaml`
3. Assigns every location to the municipality it falls in
4. Counts how many locations of each category exist per municipality
5. Downloads population figures per municipality
6. Ranks municipalities by population and separately by each category's count, then calculates the difference between the two ranks

## Setup

You need Python 3.10 or newer installed (this was built and tested with Python 3.13).

1. Open a terminal in this folder

2. Create a virtual environment:
       python -m venv venv

3. Activate it. On Windows:
       .\venv\Scripts\activate

   On Mac/Linux:
       source venv/bin/activate

4. Install the required packages:
       pip install -r requirements.txt

## Defining categories

Before running the pipeline, check `config.yaml` to see which categories will be collected. Each category needs a name and one or more matching OpenStreetMap tags. You can add, remove, or change categories here at any time. No other files need to be adjusted.
       
## Running it

Make sure the virtual environment is activated (you should see `(venv)` at the start of your terminal line), then:
    python main.py

This runs everything from start to finish. It takes around 30 to 60 minutes, because of the OpenStreetMap download step.

## Where to find things

- `data/final/mismatch_results.gpkg` — the final result, open this in QGIS to see the map
- `data/interim/points_with_municipality.gpkg` — every individual location (shop, doctor, etc.), filterable by category
- `data/interim/category_counts_per_municipality.csv` — raw counts per municipality, no ranking
- `data/raw/osm_raw_points.csv` — the raw OpenStreetMap download, before anything else was done to it
- `config.yaml` — edit this to add or remove categories, then run `python main.py` again



