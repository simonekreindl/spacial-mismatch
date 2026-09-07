import requests
import pandas as pd

# This script downloads current total population per municipality from SURS
# using the PxWeb API (SiStat database).

# Source: Statistical Office of the Republic of Slovenia (SURS)
# Dataset: Population by MUNICIPALITIES, HALF-YEAR and AGE (table 05C4003S)

url = "https://pxweb.stat.si/SiStatData/api/v1/en/Data/05C4003S.px"

# Defines which data to request: all municipalities, total population (all ages), most recent period
query = {
    "query": [
        {
            "code": "OBČINE",  # municipality
            "selection": {
                "filter": "all",
                "values": ["*"]
            }
        },
        {
            "code": "STAROST",  # age - "999" means all ages combined
            "selection": {
                "filter": "item",
                "values": ["999"]
            }
        },
        {
            "code": "POLLETJE",  # half-year period
            "selection": {
                "filter": "item",
                "values": ["2026H1"]
            }
        }
    ],
    "response": {
        "format": "json"
    }
}

response = requests.post(url, json=query)
data = response.json()

# Extract municipality code and population from each result entry
rows = []
for item in data["data"]:
    sifra_obcine = item["key"][0]
    population = item["values"][0]
    rows.append({"sifra_obcine": sifra_obcine, "population": population})

df = pd.DataFrame(rows)

# Exclude Slovenia as a whole (code "0"), keep only individual municipalities
df = df[df["sifra_obcine"] != "0"]

print(df.head())
print(f"Number of municipalities: {len(df)}")

# Save result to CSV
df.to_csv("population_per_municipality.csv", index=False, encoding="utf-8")
print("Saved as population_per_municipality.csv")