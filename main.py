import subprocess
import sys

# This script runs the full pipeline in order

steps = [
    "src/download_municipalities.py",
    "src/fetch_osm_data.py",
    "src/spatial_join.py",
    "src/count_categories.py",
    "src/download_population.py",
    "src/merge_data.py",
    "src/calculate_mismatch.py",
]

for step in steps:
    print(f"\n=== Running {step} ===")
    subprocess.run([sys.executable, step], check=True)

print("\nPipeline complete. Final result saved to data/final/mismatch_results.gpkg")