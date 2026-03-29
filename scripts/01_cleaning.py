import pandas as pd
import numpy as np

# --- LOAD DATA ----------------------------------------------------------------
trainings = pd.read_csv("data/processed/running_data.csv")

# --- DROP COLUMNS -------------------------------------------------------------
trainings = trainings.drop([
    "fuente", "version_watch", "hora_fin",
    "calorias_basales", "calorias_totales"
], axis=1)

# --- RENAME COLUMNS TO ENGLISH ------------------------------------------------
trainings = trainings.rename(columns={
    "fecha"            : "date",
    "hora_inicio"      : "start_time",
    "duracion_min"     : "duration_min",
    "distancia_km"     : "distance_km",
    "calorias_activas" : "active_calories",
    "fc_promedio"      : "avg_heart_rate",
    "fc_maxima"        : "max_heart_rate",
    "fc_minima"        : "min_heart_rate",
    "temperatura_c"    : "temperature_c",
    "humedad_pct"      : "humidity_pct",
    "elevacion_m"      : "elevation_m",
    "indoor"           : "indoor",
    "num_pausas"       : "num_pauses",
    "tiempo_pausa_min" : "pause_duration_min",
    "ritmo_min_km"     : "pace_min_km"
})

# --- FILTER OUT FALSE/ERRONEOUS RECORDS ---------------------------------------
trainings = trainings[trainings["distance_km"] >= 0.9]    # remove very short sessions
trainings = trainings[trainings["duration_min"] >= 5]     # remove very short sessions
trainings = trainings[trainings["pace_min_km"] <= 15]     # remove unrealistic pace

# --- CREATE DATETIME COLUMN ---------------------------------------------------
trainings["datetime"] = pd.to_datetime(
    trainings["date"].astype(str) + " " + trainings["start_time"]
)

trainings = trainings.drop(["date", "start_time"], axis=1)

# --- ENRICH DATASET -----------------------------------------------------------
# Day of the week
trainings["day_of_week"] = trainings["datetime"].dt.day_name()

# Month and year
trainings["month"] = trainings["datetime"].dt.month_name()
trainings["year"]  = trainings["datetime"].dt.year

# Time of day
trainings["time_of_day"] = pd.cut(
    trainings["datetime"].dt.hour,
    bins=[0, 12, 17, 24],
    labels=["morning", "afternoon", "evening"],
    include_lowest=True
)

# HR: sessions with and without heart rate data
trainings["hr_available"] = np.where(
    trainings["avg_heart_rate"].isna(), "without_hr", "with_hr"
)

# --- SAVE  --------------------------------------------------------------------
trainings.to_csv("data/processed/running_clean.csv", index=False)
