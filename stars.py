import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, timezone
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from astral.sun import sun
from astral import LocationInfo
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u

try:
    # Load locations
    with open("locations.json") as f:
        LOCATIONS = json.load(f)

    # Load stars and constellations
    with open("sky_objects.json") as f:
        SKY_DATA = json.load(f)
except FileNotFoundError as e:
    print(f"Error loading data files: Please run get_locations.py and get_stars.py first to generate data.\n{e}")
    exit(1)

def get_sun_times(lat, lon):
    location = LocationInfo(latitude=lat, longitude=lon)
    s = sun(location.observer, date=datetime.now(timezone.utc))
    return s["sunset"], s["sunrise"] + timedelta(days=1)

def compute_visible_objects(lat, lon):
    sunset, sunrise = get_sun_times(lat, lon)
    location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg)
    time_range = [sunset + timedelta(minutes=30 * i) for i in range(int((sunrise - sunset).total_seconds() // 1800))]

    visible_objects = {}
    for obj in SKY_DATA["objects"]:
        coord = SkyCoord(ra=obj["ra"] * u.deg, dec=obj["dec"] * u.deg)
        for t in time_range:
            altaz = coord.transform_to(AltAz(obstime=Time(t), location=location))
            if altaz.alt.deg > 0:
                visible_objects[obj["name"]] = (coord.ra.deg, coord.dec.deg)
                break
    return visible_objects

def plot_ra_dec_sky(visible_objects, frame):
    fig, ax = plt.subplots(figsize=(15, 5), facecolor='black')
    ax.set_facecolor('black')
    ax.set_title("RA/Dec Sky Map (Visible Tonight)", color='red')
    ax.set_xlabel("Right Ascension (°)", color='red')
    ax.set_ylabel("Declination (°)", color='red')
    ax.set_xlim(360, 0)
    ax.set_ylim(-90, 90)

    for name, (ra_deg, dec_deg) in visible_objects.items():
        ax.plot(ra_deg, dec_deg, 'ro', markersize=4)

    for const in SKY_DATA.get("constellations", []):
        star_names = const["stars"]
        for i in range(len(star_names) - 1):
            a, b = star_names[i], star_names[i + 1]
            if a in visible_objects and b in visible_objects:
                ra1, dec1 = visible_objects[a]
                ra2, dec2 = visible_objects[b]
                if abs(ra1 - ra2) < 180:
                    ax.plot([ra1, ra2], [dec1, dec2], linestyle="--", alpha=0.5, color='red')

    ax.tick_params(colors='red')
    ax.grid(True, color='gray', linestyle='--', alpha=0.3)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

def update_plot():
    lat = float(lat_entry.get() or 0)
    lon = float(lon_entry.get() or 0)

    for widget in plot_frame.winfo_children():
        widget.destroy()

    visible = compute_visible_objects(lat, lon)
    plot_ra_dec_sky(visible, plot_frame)

def filter_locations(event):
    search = location_var.get().lower()
    filtered = [name for name in LOCATIONS if search in name.lower()]
    location_menu['values'] = filtered
    if filtered:
        location_menu.event_generate('<Down>')

def update_coords_from_selection(event=None):
    selected = location_var.get()
    if selected in LOCATIONS:
        lat, lon = LOCATIONS[selected]
        lat_entry.delete(0, tk.END)
        lon_entry.delete(0, tk.END)
        lat_entry.insert(0, str(lat))
        lon_entry.insert(0, str(lon))

def on_closing():
    plt.close('all')  # Close any open matplotlib figures
    root.destroy()    # Destroy the Tk root window
    # Optionally: exit explicitly
    import sys
    sys.exit(0)



# GUI Setup
root = tk.Tk()
root.title("RA/Dec Night Sky Viewer")
root.configure(bg='black')

# Fonts and styles
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", fieldbackground='black', background='black', foreground='red')
style.configure("TLabel", background='black', foreground='red')
style.configure("TButton", background='black', foreground='red')

# Searchable location dropdown
location_var = tk.StringVar()
location_menu = ttk.Combobox(root, textvariable=location_var)
location_menu['values'] = list(LOCATIONS.keys())
location_menu.set("Custom")
location_menu.bind("<<ComboboxSelected>>", update_coords_from_selection)
location_menu.bind("<Return>", filter_locations)
location_menu.pack(pady=5)

# Manual coordinate entry
coords_frame = tk.Frame(root, bg='black')
coords_frame.pack()

tk.Label(coords_frame, text="Latitude:", bg='black', fg='red').grid(row=0, column=0)
lat_entry = tk.Entry(coords_frame, bg='black', fg='red', insertbackground='red')
lat_entry.grid(row=0, column=1)
lat_entry.insert(0, "0")

tk.Label(coords_frame, text="Longitude:", bg='black', fg='red').grid(row=1, column=0)
lon_entry = tk.Entry(coords_frame, bg='black', fg='red', insertbackground='red')
lon_entry.grid(row=1, column=1)
lon_entry.insert(0, "0")

tk.Button(root, text="Plot Night Sky", command=update_plot, bg='black', fg='red').pack(pady=5)

plot_frame = tk.Frame(root, bg='black')
plot_frame.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)


root.mainloop()
