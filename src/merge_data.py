import pandas as pd

# This script merges population and category counts into one table per municipality (key: sifra_obcine)

population = pd.read_csv("../data/raw/population_per_municipality.csv", dtype={"sifra_obcine": str})
counts = pd.read_csv("../data/interim/category_counts_per_municipality.csv", dtype={"sifra_obcine": str})

# Align municipality code format between files
population["sifra_obcine"] = population["sifra_obcine"].str.lstrip("0")
counts["sifra_obcine"] = counts["sifra_obcine"].str.lstrip("0")

# Join counts onto population
merged = pd.merge(population, counts, on="sifra_obcine", how="left")
merged = merged.fillna(0)

print(merged.head())
print(f"Number of municipalities: {len(merged)}")
print(f"Missing population values: {merged['population'].isna().sum()}")

# Save result to CSV
merged.to_csv("../data/interim/merged_municipality_data.csv", index=False, encoding="utf-8")
print("Saved as merged_municipality_data.csv")