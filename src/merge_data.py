import pandas as pd
import os

# This script merges population and category counts into one table per municipality (key: sifra_obcine)

# Make file paths work no matter where this script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

population = pd.read_csv(os.path.join(DATA_DIR, "raw", "population_per_municipality.csv"), dtype={"sifra_obcine": str})
counts = pd.read_csv(os.path.join(DATA_DIR, "interim", "category_counts_per_municipality.csv"), dtype={"sifra_obcine": str})

# Align municipality code format between files
population["sifra_obcine"] = population["sifra_obcine"].str.lstrip("0")
counts["sifra_obcine"] = counts["sifra_obcine"].str.lstrip("0")

# Remove duplicate name column before merging
counts = counts.drop(columns=["municipality_name"])

# Join counts onto population
merged = pd.merge(population, counts, on="sifra_obcine", how="left")
merged = merged.fillna(0)

print(merged.head())
print(f"Number of municipalities: {len(merged)}")
print(f"Missing population values: {merged['population'].isna().sum()}")

# Save result to CSV
merged.to_csv(os.path.join(DATA_DIR, "interim", "merged_municipality_data.csv"), index=False, encoding="utf-8")
print("Saved as merged_municipality_data.csv")