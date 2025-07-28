### get_stars.py
### This script queries the SIMBAD database for star coordinates based on HIP numbers
### and combines them with constellation data from a Stellarium index file.
### The stellarium file was retrieved from the Stellarium GitHub repository.
### https://github.com/Stellarium/stellarium/blob/master/skycultures/modern_iau/index.json

### to use, simply run this script in the same directory as the stellarium_IAU_index.json file
### it will create sky_objects.json with the parsed data

import json
from astroquery.simbad import Simbad
from time import sleep

print("Starting star coordinate extraction... (this may take a while)")

# Constants
INDEX_FILE = "stellarium_IAU_index.json"
OUTPUT_FILE = "sky_objects.json"

# Setup SIMBAD query
Simbad.TIMEOUT = 60
simbad = Simbad()
simbad.add_votable_fields("ra", "dec")

# 1. Load Stellarium IAU index.json
index = json.load(open(INDEX_FILE))

# 2. Extract all unique HIP numbers from all constellation lines
hip_set = set()
for constellation in index["constellations"]:
    for line in constellation.get("lines", []):
        hip_set.update(line)

hip_list = sorted(hip_set)
print(f"Found {len(hip_list)} unique HIP numbers.")

# 3. Query SIMBAD for each HIP number to get coordinates
objects = []
for hip in hip_list:
    identifier = f"HIP {hip}"
    try:
        res = simbad.query_object(identifier)
        if res:
            ra = float(res["ra"][0])
            dec = float(res["dec"][0])
            objects.append({
                "name": identifier,
                "ra": ra,
                "dec": dec
            })
        else:
            print(f"Not found: {identifier}")
    except Exception as e:
        print(f"Error querying {identifier}: {e}")
    sleep(0.1)  # polite delay to avoid hammering CDS
    print(f"Queried {len(objects)} stars so far...", end='\r')

print(f"Queried {len(objects)} stars with coordinates.")

# 4. Build constellations with HIP star lists
constellations_out = []
for constellation in index["constellations"]:
    const_id = constellation["id"]
    lines = constellation.get("lines", [])

    # Flatten HIP numbers and deduplicate
    hip_numbers = set()
    for line in lines:
        hip_numbers.update(line)

    # Format as "HIP NNNN"
    hip_names = [f"HIP {num}" for num in sorted(hip_numbers)]

    constellations_out.append({
        "name": const_id,
        "stars": hip_names
    })

print(f"Processed {len(constellations_out)} constellations.")

# 5. Save combined output to one JSON file
combined_data = {
    "objects": objects,
    "constellations": constellations_out
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(combined_data, f, indent=2)

print(f"✅ Saved combined data to {OUTPUT_FILE}")
