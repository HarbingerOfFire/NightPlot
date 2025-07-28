### get_locations.py
### this is used to generate a JSON file locations.json
### which contains observatory locations in lat/lon format
### for use in the stars.py GUI

### to use, simply run this script in the same directory as the ObsCodes.csv file
### it will create locations.json with the parsed data

import csv
import math

# Constants for WGS84 Earth ellipsoid
f = 1 / 298.257223563  # flattening
e2 = 2 * f - f ** 2    # eccentricity squared

def geodetic_latitude_from_parallax_constants(rho_sin_phi_prime, rho_cos_phi_prime):
    # Geocentric latitude (radians)
    phi_prime = math.atan2(rho_sin_phi_prime, rho_cos_phi_prime)
    # Convert geocentric latitude to geodetic latitude using Earth's eccentricity
    tan_phi = math.tan(phi_prime) / (1 - e2)
    phi = math.atan(tan_phi)
    return math.degrees(phi)

def normalize_longitude(lon_deg):
    # Normalize longitude to [-180, 180]
    while lon_deg > 180:
        lon_deg -= 360
    while lon_deg < -180:
        lon_deg += 360
    return lon_deg

def scale_longitude(raw_lon):
    # Heuristic: if longitude is too large (> 360), assume it's scaled by 1000
    if abs(raw_lon) > 360:
        return raw_lon / 1000.0
    return raw_lon

def parse_observatories_csv(file_path):
    observatories = {}

    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header

        for row in reader:
            if len(row) < 5:
                continue  # skip malformed lines

            code = row[0].strip()
            try:
                raw_lon = float(row[1].strip())
                cos_val = float(row[2].strip())
                sin_val = float(row[3].strip())
                name = ', '.join([r.strip() for r in row[4:] if r.strip()])
            except ValueError:
                continue  # skip if conversion fails

            # Convert parallax constants to geodetic latitude
            lat_deg = geodetic_latitude_from_parallax_constants(sin_val, cos_val)
            # Scale longitude if needed
            lon_deg = scale_longitude(raw_lon)
            # Normalize longitude to [-180,180]
            lon_deg = normalize_longitude(lon_deg)

            observatories[name] = [round(lat_deg, 6), round(lon_deg, 6)]

    return observatories

# Example usage
observatory_data = parse_observatories_csv("ObsCodes.csv")

import json
json.dump(observatory_data, open("locations.json", "w"), indent=2)


print(f"Parsed {len(observatory_data)} observatories.")