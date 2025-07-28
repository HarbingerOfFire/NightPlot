# NightPlot

NightPlot is a Python GUI tool for visualizing the night sky, showing visible stars and constellations for any location and date. It uses real observatory locations and star data from the SIMBAD database and Stellarium's IAU constellation index.

## Features

- Interactive sky map of visible stars and constellations for any location.
- Observatory location search and manual latitude/longitude entry.
- Data sourced from SIMBAD and Stellarium.

## Setup

1. **Install dependencies:**
`pip install -r requirements.txt`

2. **Prepare data:**

- Place `ObsCodes.csv` and `stellarium_IAU_index.json` in the project directory.
- Run the following scripts to generate required data files:
  ```
  python3 get_locations.py
  python3 get_stars.py
  ```

3. **Run the GUI:**
`python stars.py`

## Files

- `get_locations.py`: Generates `locations.json` from `ObsCodes.csv`.
- `get_stars.py`: Generates `sky_objects.json` from `stellarium_IAU_index.json` and SIMBAD.
- `stars.py`: Main GUI application.
- `ObsCodes.csv`: Observatory codes and locations.
- `stellarium_IAU_index.json`: Constellation line data.
- `requirements.txt`: Python dependencies.

## Credits

- Star and constellation data: [Stellarium](https://github.com/Stellarium/stellarium)
- Star coordinates: [SIMBAD Astronomical Database](http://simbad.u-strasbg.fr/simbad/)

---

**NightPlot** is for educational and visualization purposes.