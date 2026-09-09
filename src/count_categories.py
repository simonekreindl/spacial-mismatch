import geopandas as gpd
import os

# This script counts how many points of each category exist per municipality,
# turning the point-level join result into a per-municipality summary table

# Make file paths work no matter where this script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

joined = gpd.read_file(os.path.join(DATA_DIR, "interim", "points_with_municipality.gpkg"))

# Count points per municipality + category combination
counts = joined.groupby(["sifra_obcine", "municipality_name", "category"]).size().reset_index(name="count")

# Reshape so each category becomes its own column
counts_wide = counts.pivot_table(
    index=["sifra_obcine", "municipality_name"],
    columns="category",
    values="count",
    fill_value=0
).reset_index()

print(counts_wide.head())

# Save result to CSV
counts_wide.to_csv(os.path.join(DATA_DIR, "interim", "category_counts_per_municipality.csv"), index=False, encoding="utf-8")
print("Saved as category_counts_per_municipality.csv")