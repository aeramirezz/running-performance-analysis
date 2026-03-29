import xml.etree.ElementTree as ET
import pandas as pd
import os

# --- CONFIG -------------------------------------------------------------------
XML_PATH    = "exportar.xml"
OUTPUT_PATH = "running_data_v2.csv"

# --- LOAD XML -----------------------------------------------------------------
tree = ET.parse(XML_PATH)
root = tree.getroot()

# --- EXTRACT WORKOUTS ---------------------------------------------------------
workouts = []

for workout in root.findall("Workout"):
    activity = workout.get("workoutActivityType", "")
    if "Running" not in activity:
        continue

    row = {
        "fecha"            : workout.get("startDate", "")[:10],
        "hora_inicio"      : workout.get("startDate", "")[11:19],
        "hora_fin"         : workout.get("endDate", "")[11:19],
        "duracion_min"     : round(float(workout.get("duration", 0)), 2),
        "fuente"           : workout.get("sourceName", ""),
        "version_watch"    : workout.get("sourceVersion", ""),
        "distancia_km"     : None,
        "calorias_activas" : None,
        "calorias_basales" : None,
        "calorias_totales" : None,
        "fc_promedio"      : None,
        "fc_maxima"        : None,
        "fc_minima"        : None,
        "temperatura_c"    : None,
        "humedad_pct"      : None,
        "elevacion_m"      : None,
        "indoor"           : None,
        "num_pausas"       : 0,
        "tiempo_pausa_min" : 0.0,
    }

    # --- METADATA (weather, elevation, indoor) --------------------------------
    for meta in workout.findall("MetadataEntry"):
        key   = meta.get("key", "")
        value = meta.get("value", "")

        if key == "HKWeatherTemperature":
            try:
                f = float(value.split()[0])
                row["temperatura_c"] = round((f - 32) * 5 / 9, 1)
            except:
                pass

        elif key == "HKWeatherHumidity":
            try:
                h = float(value.split()[0])
                row["humedad_pct"] = round(h / 100, 1)
            except:
                pass

        elif key == "HKElevationAscended":
            try:
                cm = float(value.split()[0])
                row["elevacion_m"] = round(cm / 100, 1)
            except:
                pass

        elif key == "HKIndoorWorkout":
            row["indoor"] = value == "1"

    # --- WORKOUT STATISTICS (distance, calories, heart rate) ------------------
    for stats in workout.findall("WorkoutStatistics"):
        tipo = stats.get("type", "")
        unit = stats.get("unit", "")

        if "DistanceWalkingRunning" in tipo or "DistanceRunning" in tipo:
            val = stats.get("sum")
            if val:
                km = float(val)
                if "mi" in unit.lower():
                    km = km * 1.60934
                row["distancia_km"] = round(km, 3)

        elif "ActiveEnergyBurned" in tipo:
            val = stats.get("sum")
            if val:
                row["calorias_activas"] = round(float(val), 1)

        elif "BasalEnergyBurned" in tipo:
            val = stats.get("sum")
            if val:
                row["calorias_basales"] = round(float(val), 1)

        elif "HeartRate" in tipo:
            avg = stats.get("average")
            mx  = stats.get("maximum")
            mn  = stats.get("minimum")
            if avg: row["fc_promedio"] = round(float(avg), 1)
            if mx:  row["fc_maxima"]   = round(float(mx), 1)
            if mn:  row["fc_minima"]   = round(float(mn), 1)

    if row["calorias_activas"] and row["calorias_basales"]:
        row["calorias_totales"] = round(
            row["calorias_activas"] + row["calorias_basales"], 1
        )

    # --- PAUSES ---------------------------------------------------------------
    pause_times = []
    last_pause  = None

    for event in workout.findall("WorkoutEvent"):
        etype = event.get("type", "")
        edate = event.get("date", "")

        if "Paused" in etype or etype == "HKWorkoutEventTypePause":
            try:
                last_pause = pd.to_datetime(edate[:19])
            except:
                pass

        elif ("Resumed" in etype or "Resume" in etype) and last_pause is not None:
            try:
                resumed       = pd.to_datetime(edate[:19])
                pause_duration = (resumed - last_pause).total_seconds() / 60
                if 0 < pause_duration < 60:
                    pause_times.append(pause_duration)
                last_pause = None
            except:
                pass

    row["num_pausas"]       = len(pause_times)
    row["tiempo_pausa_min"] = round(sum(pause_times), 2)

    # --- PACE -----------------------------------------------------------------
    if row["distancia_km"] and row["distancia_km"] > 0:
        row["ritmo_min_km"] = round(row["duracion_min"] / row["distancia_km"], 2)
    else:
        row["ritmo_min_km"] = None

    workouts.append(row)

# --- BUILD DATAFRAME AND SAVE -------------------------------------------------
df = pd.DataFrame(workouts)
df = df.sort_values("fecha").reset_index(drop=True)
df.to_csv(OUTPUT_PATH, index=False)