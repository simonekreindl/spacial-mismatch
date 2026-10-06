import geopandas as gpd
import pandas as pd
import os
import yaml

# This script calculates spatial mismatch scores per municipality and saves the final
# result as a GeoPackage, combining the data with municipality boundaries.

# Make file paths work no matter where this script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

df = pd.read_csv(os.path.join(DATA_DIR, "interim", "merged_municipality_data.csv"))

# Rank municipalities by population (rank 1 = highest population)
df["population_rank"] = df["population"].rank(ascending=False)

# Read the category names from config
with open(os.path.join(SCRIPT_DIR, "..", "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

category_columns_wanted = [
    subcat
    for midcats in config["categories"].values()
    for subcat in midcats.keys()
]

category_columns = category_columns_wanted

# Collect the new columns in a dictionary and add them to the table at once
new_columns = {}

for cat in category_columns:
    # Rank all municipalities by the number of locations (rank 1 = most)
    cat_rank = df[cat].rank(ascending=False)

    # Population rank minus category rank: positive means more locations than
    # the population suggests, negative means fewer
    signed = df["population_rank"] - cat_rank

    # Save the rank, the mismatch size (absolute value) and the signed mismatch
    new_columns[f"{cat}_rank"] = cat_rank
    new_columns[f"mismatch_{cat}"] = signed.abs()
    new_columns[f"mismatch_{cat}_signed"] = signed

df = pd.concat([df, pd.DataFrame(new_columns)], axis=1)

print(df.head())

# Combine with municipality boundaries to produce a mappable final result
boundaries = gpd.read_file(os.path.join(DATA_DIR, "raw", "municipalities.gpkg"))
boundaries["sifra_obcine"] = boundaries["sifra_obcine"].astype(str)
df["sifra_obcine"] = df["sifra_obcine"].astype(str)

final = boundaries.merge(df, on="sifra_obcine", how="left")

# Save as a GeoPackage file
final.to_file(os.path.join(DATA_DIR, "final", "mismatch_results.gpkg"), driver="GPKG")
print("Saved as mismatch_results.gpkg")