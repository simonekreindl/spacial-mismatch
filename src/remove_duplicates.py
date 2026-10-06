import geopandas as gpd
import os
import csv

# This script finds and removes likely duplicate OSM entries: the same
# name and category, within 50 meters of each other in the same
# municipality. Also saves a clean, duplicate-free CSV of all locations to final.

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

# Bus stops and parcel lockers legitimately repeat nearby,
# so these categories are excluded from the duplicate check
EXCLUDED_FROM_DUPLICATE_CHECK = {"public_transport_stops", "parcel_lockers"}
DUPLICATE_DISTANCE_THRESHOLD_M = 50

points = gpd.read_file(os.path.join(DATA_DIR, "interim", "points_with_municipality.gpkg"))
points = points.to_crs(epsg=3794)

to_remove = set()
removed_log = []

# Compare entries one municipality at a time
for muni in points["municipality_name"].unique():
    subset = points[points["municipality_name"] == muni]

    # Only compare entries that share the same name and category
    for (name, category), group in subset.groupby(["name", "category"]):
        if name == "unnamed" or len(group) < 2 or category in EXCLUDED_FROM_DUPLICATE_CHECK:
            continue

        # Check every pair within this group for closeness
        indices = group.index.tolist()
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                idx1, idx2 = indices[i], indices[j]
                if idx1 in to_remove or idx2 in to_remove:
                    continue

                # If they're close enough, treat the second one as a duplicate
                dist = points.loc[idx1, "geometry"].distance(points.loc[idx2, "geometry"])
                if dist < DUPLICATE_DISTANCE_THRESHOLD_M:
                    to_remove.add(idx2)
                    removed_log.append({
                        "municipality": muni,
                        "name": name,
                        "category": category,
                        "kept_osm_id": points.loc[idx1, "osm_id"],
                        "removed_osm_id": points.loc[idx2, "osm_id"],
                        "distance_m": round(dist, 1)
                    })

cleaned = points.drop(index=to_remove)
print(f"Removed {len(to_remove)} likely duplicate entries")

# Overwrite the interim file so later steps use the cleaned data
cleaned.to_file(os.path.join(DATA_DIR, "interim", "points_with_municipality.gpkg"), driver="GPKG")

# Also save a plain CSV for opening directly in Excel in final
cleaned.drop(columns="geometry").to_csv(
    os.path.join(DATA_DIR, "final", "all_locations.csv"),
    index=False, encoding="utf-8"
)
print("Saved as points_with_municipality.gpkg and all_locations.csv")

# Remove the log from any earlier run, so it always matches this run
log_path = os.path.join(DATA_DIR, "interim", "removed_duplicates.log")
if os.path.exists(log_path):
    os.remove(log_path)

# Only written if at least one duplicate was found
if removed_log:
    log_path = os.path.join(DATA_DIR, "interim", "removed_duplicates.log")
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=removed_log[0].keys())
        writer.writeheader()
        writer.writerows(removed_log)
    print("Details saved to removed_duplicates.log")