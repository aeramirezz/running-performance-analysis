import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_absolute_error

# --- CONFIG -------------------------------------------------------------------
CLEAN_CSV = "data/processed/running_clean.csv"
PLOTS_DIR = "plots"

os.makedirs(PLOTS_DIR, exist_ok=True)

# --- LOAD DATA ----------------------------------------------------------------
trainings = pd.read_csv(CLEAN_CSV)

target = "active_calories"
df     = trainings.dropna(subset=[target])

# --- MODEL A: predict calories from distance ----------------------------------
features_a = ["distance_km", "pace_min_km", "elevation_m", "temperature_c"]

X_a         = df[features_a]
y_a         = df[target]
imputer_a   = SimpleImputer(strategy="mean")
X_a_imputed = imputer_a.fit_transform(X_a)

X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(
    X_a_imputed, y_a, test_size=0.2, random_state=42
)

model_a = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model_a.fit(X_train_a, y_train_a)

y_pred_a = model_a.predict(X_test_a)
r2_a     = r2_score(y_test_a, y_pred_a)
mae_a    = mean_absolute_error(y_test_a, y_pred_a)

print(f"\nModel A — Distance-based:")
print(f"  R²  : {r2_a:.3f}")
print(f"  MAE : {mae_a:.1f} kcal")

# --- MODEL B: predict calories from duration ----------------------------------
features_b = ["duration_min", "pace_min_km", "elevation_m", "temperature_c"]

X_b         = df[features_b]
y_b         = df[target]
imputer_b   = SimpleImputer(strategy="mean")
X_b_imputed = imputer_b.fit_transform(X_b)

X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X_b_imputed, y_b, test_size=0.2, random_state=42
)

model_b = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model_b.fit(X_train_b, y_train_b)

y_pred_b = model_b.predict(X_test_b)
r2_b     = r2_score(y_test_b, y_pred_b)
mae_b    = mean_absolute_error(y_test_b, y_pred_b)

print(f"\nModel B — Duration-based:")
print(f"  R²  : {r2_b:.3f}")
print(f"  MAE : {mae_b:.1f} kcal")

# --- FEATURE IMPORTANCE -------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

imp_a = pd.DataFrame({
    "feature"    : features_a,
    "importance" : model_a.feature_importances_
}).sort_values("importance", ascending=True)

imp_b = pd.DataFrame({
    "feature"    : features_b,
    "importance" : model_b.feature_importances_
}).sort_values("importance", ascending=True)

axes[0].barh(imp_a["feature"], imp_a["importance"], color="#30D158")
axes[0].set_title("Feature Importance — Model A (Distance)", fontsize=13)
axes[0].set_xlabel("Importance")

axes[1].barh(imp_b["feature"], imp_b["importance"], color="#30D158")
axes[1].set_title("Feature Importance — Model B (Duration)", fontsize=13)
axes[1].set_xlabel("Importance")

plt.suptitle("Calorie Prediction Models — Feature Importance", fontsize=15)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/19_feature_importance.png", dpi=150)
plt.show()

# --- PREDICTED VS ACTUAL ------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].scatter(y_test_a, y_pred_a, alpha=0.6, color="#30D158", s=40)
axes[0].plot([y_test_a.min(), y_test_a.max()],
             [y_test_a.min(), y_test_a.max()],
             color="#FF375F", linewidth=2, linestyle="--")
axes[0].set_title(f"Model A — Predicted vs Actual (R²={r2_a:.2f})", fontsize=13)
axes[0].set_xlabel("Actual Calories (kcal)")
axes[0].set_ylabel("Predicted Calories (kcal)")

axes[1].scatter(y_test_b, y_pred_b, alpha=0.6, color="#30D158", s=40)
axes[1].plot([y_test_b.min(), y_test_b.max()],
             [y_test_b.min(), y_test_b.max()],
             color="#FF375F", linewidth=2, linestyle="--")
axes[1].set_title(f"Model B — Predicted vs Actual (R²={r2_b:.2f})", fontsize=13)
axes[1].set_xlabel("Actual Calories (kcal)")
axes[1].set_ylabel("Predicted Calories (kcal)")

plt.suptitle("Calorie Prediction Models", fontsize=15)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/20_predicted_vs_actual.png", dpi=150)
plt.show()

# --- SIMULATION ---------------------------------------------------------------
print("\n--- Calorie Simulation ---")

# Model A: I plan to run 7km at 6:00 min/km
sim_a = imputer_a.transform([[7.0, 6.0, 30.0, 22.0]])
cal_a = model_a.predict(sim_a)[0]
print(f"  Model A | 7km, pace 6:00, 30m elevation, 22°C → {cal_a:.0f} kcal predicted")

# Model B: I plan to run 45 minutes at 6:00 min/km
sim_b = imputer_b.transform([[45.0, 6.0, 30.0, 22.0]])
cal_b = model_b.predict(sim_b)[0]
print(f"  Model B | 45min, pace 6:00, 30m elevation, 22°C → {cal_b:.0f} kcal predicted")

# --- OVERFITTING CHECK --------------------------------------------------------
r2_train_a = r2_score(y_train_a, model_a.predict(X_train_a))
r2_train_b = r2_score(y_train_b, model_b.predict(X_train_b))

print(f"\nOverfitting Check:")
print(f"  Model A | Train R²: {r2_train_a:.3f} | Test R²: {r2_a:.3f} | Gap: {r2_train_a - r2_a:.3f}")
print(f"  Model B | Train R²: {r2_train_b:.3f} | Test R²: {r2_b:.3f} | Gap: {r2_train_b - r2_b:.3f}")






