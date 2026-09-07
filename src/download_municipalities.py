import geopandas as gpd

# This script downloads the official boundaries of all 212 Slovenian municipalities

# Source: Geodetska uprava Republike Slovenije (GURS), Register prostorskih enot (RPE)
# WFS layer: SI.GURS.RPE:OBCINE - municipality boundaries
# License: CC-BY 4.0

# Direct data query from GURS's server
# Reference frame: EPSG:3794 (Slovenian national coordinate system)
wfs_url = (
    "https://ipi.eprostor.gov.si/wfs-si-gurs-rpe/wfs"
    "?service=WFS"
    "&version=2.0.0"
    "&request=GetFeature"
    "&typeName=SI.GURS.RPE:OBCINE"
    "&outputFormat=application/json"
    "&srsName=EPSG:3794"
)

# Download the data into a GeoDataFrame
gdf = gpd.read_file(wfs_url)

# Keep only relevant columns, rename to consistent naming
gdf = gdf[["SIFRA", "NAZIV", "geometry"]]
gdf = gdf.rename(columns={"SIFRA": "sifra_obcine", "NAZIV": "municipality_name"})

print(f"Number of municipalities: {len(gdf)}")
print(gdf.head())

# Save as a GeoPackage file
gdf.to_file("../data/raw/municipalities.gpkg", driver="GPKG")
print("Saved as municipalities.gpkg")