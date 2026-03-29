import os
import xml.etree.ElementTree as ET
import pandas as pd

# --- CONFIG -------------------------------------------------------------------
GPX_FOLDER      = "data/raw/gpx"
ROUTES_OUTPUT   = "data/processed/routes.csv"
POINTS_OUTPUT   = "data/processed/route_points.csv"

# --- PARSE GPX FILES ----------------------------------------------------------
routes = []
points = []

gpx_files = [f for f in os.listdir(GPX_FOLDER) if f.endswith(".gpx")]

for filename in sorted(gpx_files):
    filepath = os.path.join(GPX_FOLDER, filename)

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        ns   = {"gpx": "http://www.topografix.com/GPX/1/1"}

        # extract all track points
        trkpts = root.findall(".//gpx:trkpt", ns)
        if not trkpts:
            continue

        # date comes from the first track point timestamp
        first_time = trkpts[0].find("gpx:time", ns)
        if first_time is None:
            continue
        date = first_time.text[:10]

        # --- ROUTE SUMMARY (one row per file) ---------------------------------
        elevations = []
        speeds     = []
        lats       = []
        lons       = []
        timestamps = []

        for pt in trkpts:
            lat  = float(pt.get("lat"))
            lon  = float(pt.get("lon"))
            time = pt.find("gpx:time", ns)
            ele  = pt.find("gpx:ele", ns)

            ext   = pt.find("gpx:extensions", ns)
            speed = ext.find("gpx:speed", ns) if ext is not None else None

            lats.append(lat)
            lons.append(lon)
            elevations.append(float(ele.text) if ele is not None else None)
            speeds.append(float(speed.text) if speed is not None else None)
            timestamps.append(time.text if time is not None else None)

        # elevation gain and loss
        elev_clean = [e for e in elevations if e is not None]
        elev_gain  = 0.0
        elev_loss  = 0.0
        for i in range(1, len(elev_clean)):
            diff = elev_clean[i] - elev_clean[i - 1]
            if diff > 0:
                elev_gain += diff
            else:
                elev_loss += abs(diff)

        speeds_clean = [s for s in speeds if s is not None]

        routes.append({
            "date"          : date,
            "start_lat"     : lats[0],
            "start_lon"     : lons[0],
            "elevation_gain": round(elev_gain, 1),
            "elevation_loss": round(elev_loss, 1),
            "max_speed"     : round(max(speeds_clean), 3) if speeds_clean else None,
            "avg_speed"     : round(sum(speeds_clean) / len(speeds_clean), 3) if speeds_clean else None,
            "total_points"  : len(trkpts),
        })

        # --- ROUTE POINTS (one row per GPS point) -----------------------------
        for i, pt in enumerate(trkpts):
            lat   = float(pt.get("lat"))
            lon   = float(pt.get("lon"))
            time  = pt.find("gpx:time", ns)
            ele   = pt.find("gpx:ele", ns)
            ext   = pt.find("gpx:extensions", ns)
            speed = ext.find("gpx:speed", ns) if ext is not None else None

            points.append({
                "date"      : date,
                "timestamp" : time.text if time is not None else None,
                "lat"       : lat,
                "lon"       : lon,
                "elevation" : float(ele.text) if ele is not None else None,
                "speed"     : float(speed.text) if speed is not None else None,
            })

    except Exception as e:
        print(f"  Could not parse {filename}: {e}")

# --- SAVE ---------------------------------------------------------------------
df_routes = pd.DataFrame(routes)
df_points = pd.DataFrame(points)

df_routes.to_csv(ROUTES_OUTPUT, index=False)
df_points.to_csv(POINTS_OUTPUT, index=False)