import geopandas as gpd
import pandas as pd

# This script assigns each OSM point to the
# municipality it falls within

# Load OSM points and convert to a GeoDataFrame
points_df = pd.read_csv("../data/raw/osm_raw_points.csv")
points_gdf = gpd.GeoDataFrame(
    points_df,
    geometry=gpd.points_from_xy(points_df.lon, points_df.lat),
    crs="EPSG:4326"  # OSM coordinates come in WGS84
)

# Convert to Slovenia's national reference frame to match municipality boundaries
points_gdf = points_gdf.to_crs(epsg=3794)

# Load municipality boundaries
municipalities = gpd.read_file("../data/raw/municipalities.gpkg")

# Spatial join: for each point, find which municipality polygon it falls within
joined = gpd.sjoin(points_gdf, municipalities, how="left", predicate="within")

print(f"Assigned: {joined['sifra_obcine'].notna().sum()} of {len(joined)}")
print(f"Not assigned (edge cases / errors): {joined['sifra_obcine'].isna().sum()}")

# Save as a GeoPackage file
joined.to_file("../data/interim/points_with_municipality.gpkg", driver="GPKG")
print("Saved as points_with_municipality.gpkg")