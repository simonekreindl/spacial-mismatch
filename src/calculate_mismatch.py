import geopandas as gpd
import pandas as pd

# This script calculates spatial mismatch scores per municipality and saves the final
# result as a GeoPackage, combining the data with municipality boundaries.

df = pd.read_csv("../data/interim/merged_municipality_data.csv")

# Rank municipalities by population (rank 1 = highest population)
df["population_rank"] = df["population"].rank(ascending=False)

category_columns = ["grocery", "healthcare"]

for cat in category_columns:
    # Rank municipalities by this category's count (rank 1 = most services)
    df[f"{cat}_rank"] = df[cat].rank(ascending=False)

    # Absolute rank difference (size of the mismatch)
    df[f"mismatch_{cat}"] = (df["population_rank"] - df[f"{cat}_rank"]).abs()

    # Signed rank difference (positive = more services than expected,
    # negative = fewer services than expected)
    df[f"mismatch_{cat}_signed"] = df["population_rank"] - df[f"{cat}_rank"]

print(df.head())

# Combine with municipality boundaries to produce a mappable final result
boundaries = gpd.read_file("../data/raw/municipalities.gpkg")
boundaries["sifra_obcine"] = boundaries["sifra_obcine"].astype(str)
df["sifra_obcine"] = df["sifra_obcine"].astype(str)

final = boundaries.merge(df, on="sifra_obcine", how="left")

# Save as a GeoPackage file
final.to_file("../data/final/mismatch_results.gpkg", driver="GPKG")
print("Saved as mismatch_results.gpkg")