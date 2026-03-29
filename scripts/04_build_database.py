import pandas as pd
import sqlite3
import os

# --- CONFIG -------------------------------------------------------------------
CLEAN_CSV    = "data/processed/running_clean.csv"
ROUTES_CSV   = "data/processed/routes.csv"
POINTS_CSV   = "data/processed/route_points.csv"
DB_PATH      = "data/processed/running.db"

# --- LOAD DATA ----------------------------------------------------------------
trainings    = pd.read_csv(CLEAN_CSV)
routes       = pd.read_csv(ROUTES_CSV)
route_points = pd.read_csv(POINTS_CSV)

# --- CREATE RUN ID ------------------------------------------------------------
# run_id is a unique integer identifier for each session (1-indexed)
trainings["run_id"] = range(1, len(trainings) + 1)

# extract date from datetime for joining with routes
trainings["date"] = pd.to_datetime(trainings["datetime"]).dt.date.astype(str)

# --- BUILD TABLES -------------------------------------------------------------
# runs: core metrics for each session
runs = trainings[[
    "run_id", "datetime", "date", "distance_km", "duration_min",
    "pace_min_km", "indoor", "day_of_week", "month", "year", "time_of_day"
]]

# conditions: environmental context
conditions = trainings[[
    "run_id", "temperature_c", "humidity_pct", "elevation_m"
]]

# performance: physiological output
performance = trainings[[
    "run_id", "avg_heart_rate", "max_heart_rate", "min_heart_rate",
    "active_calories", "num_pauses", "pause_duration_min", "hr_available"
]]

# routes: join run_id from trainings using date
routes = routes.merge(trainings[["run_id", "date"]], on="date", how="left")
routes = routes[[
    "run_id", "date", "start_lat", "start_lon",
    "elevation_gain", "elevation_loss", "max_speed", "avg_speed", "total_points"
]]

# route_points: join run_id from routes using date
route_points = route_points.merge(routes[["run_id", "date"]], on="date", how="left")
route_points = route_points[[
    "run_id", "timestamp", "lat", "lon", "elevation", "speed"
]]

# --- SAVE TO SQLITE -----------------------------------------------------------
conn = sqlite3.connect(DB_PATH)

runs.to_sql("runs", conn, if_exists="replace", index=False)
conditions.to_sql("conditions", conn, if_exists="replace", index=False)
performance.to_sql("performance", conn, if_exists="replace", index=False)
routes.to_sql("routes", conn, if_exists="replace", index=False)
route_points.to_sql("route_points", conn, if_exists="replace", index=False)

conn.close()

print(f"\nDone. Database saved to: {DB_PATH}")
print(f"  runs         : {len(runs)} rows")
print(f"  conditions   : {len(conditions)} rows")
print(f"  performance  : {len(performance)} rows")
print(f"  routes       : {len(routes)} rows")
print(f"  route_points : {len(route_points)} rows")