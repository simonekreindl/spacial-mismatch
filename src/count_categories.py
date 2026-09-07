import geopandas as gpd

# This script counts how many points of each category exist per municipality,
# turning the point-level join result into a per-municipality summary table

joined = gpd.read_file("../data/interim/points_with_municipality.gpkg")

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

counts_wide.to_csv("../data/interim/category_counts_per_municipality.csv", index=False, encoding="utf-8")
print("Saved as category_counts_per_municipality.csv")