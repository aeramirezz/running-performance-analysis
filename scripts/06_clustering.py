import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# --- CONFIG -------------------------------------------------------------------
CLEAN_CSV   = "data/processed/running_clean.csv"
PLOTS_DIR   = "plots"

os.makedirs(PLOTS_DIR, exist_ok=True)

# --- LOAD DATA ----------------------------------------------------------------
trainings = pd.read_csv(CLEAN_CSV)

# --- SELECT FEATURES ----------------------------------------------------------
features = [
    "distance_km", "duration_min", "pace_min_km",
    "elevation_m", "avg_heart_rate", "active_calories",
    "num_pauses", "pause_duration_min"
]

X = trainings[features].copy()

# --- IMPUTE MISSING VALUES ----------------------------------------------------
# Replace nulls with column mean
imputer = SimpleImputer(strategy="mean")
X_imputed = imputer.fit_transform(X)

# --- SCALE FEATURES -----------------------------------------------------------
# K-Means is distance-based so all features must be on the same scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# --- ELBOW METHOD -------------------------------------------------------------
inertias = []
k_range  = range(2, 11)

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

plt.figure(figsize=(10, 5))
plt.plot(k_range, inertias, marker="o", color="#30D158", linewidth=2)
plt.title("Elbow Method — Optimal Number of Clusters", fontsize=14)
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.xticks(k_range)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/16_elbow_method.png", dpi=150)
plt.show()

print("Review the elbow plot and set K below.")

# --- SET K HERE AFTER REVIEWING THE ELBOW PLOT --------------------------------
K = 4

# --- FIT FINAL MODEL ----------------------------------------------------------
km_final = KMeans(n_clusters=K, random_state=42, n_init=10)
trainings["cluster"] = km_final.fit_predict(X_scaled)

# --- CLUSTER PROFILES ---------------------------------------------------------
# Average of each feature per cluster
cluster_profiles = trainings.groupby("cluster")[features].mean().round(2)
print("\nCluster profiles:")
print(cluster_profiles)

# --- PCA FOR VISUALIZATION ----------------------------------------------------
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

variance_explained = pca.explained_variance_ratio_ * 100
print(f"\nPCA variance explained: {variance_explained[0]:.1f}% + {variance_explained[1]:.1f}% = {sum(variance_explained):.1f}%")

pca_df = pd.DataFrame({
    "pc1"     : X_pca[:, 0],
    "pc2"     : X_pca[:, 1],
    "cluster" : trainings["cluster"].astype(str)
})

colors  = ["#30D158", "#FF375F", "#0A84FF", "#FFD60A"]
cluster_labels = ["Short & Intense", "Easy", "Treadmill", "Long Run"]

plt.figure(figsize=(10, 7))
for i in range(K):
    mask = pca_df["cluster"] == str(i)
    plt.scatter(
        pca_df.loc[mask, "pc1"],
        pca_df.loc[mask, "pc2"],
        c=colors[i], label=cluster_labels[i], alpha=0.7, s=50
    )

plt.title("Running Sessions — K-Means Clusters (PCA projection)", fontsize=14)
plt.xlabel(f"PC1 ({variance_explained[0]:.1f}% variance)")
plt.ylabel(f"PC2 ({variance_explained[1]:.1f}% variance)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/17_pca_clusters.png", dpi=150)
plt.show()

# --- CLUSTER PROFILES VISUALIZATION ------------------------------------------
trainings["cluster_label"] = trainings["cluster"].map({
    0: "Short & Intense",
    1: "Easy",
    2: "Treadmill",
    3: "Long Run"
})

cluster_order = ["Short & Intense", "Easy", "Treadmill", "Long Run"]

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# calories per cluster
for i, label in enumerate(cluster_order):
    mask = trainings["cluster_label"] == label
    axes[0].bar(i, trainings.loc[mask, "active_calories"].mean(),
                color=colors[i], label=label)
axes[0].set_title("Avg Calories Burned by Cluster", fontsize=13)
axes[0].set_ylabel("Active Calories (kcal)")
axes[0].set_xticks(range(K))
axes[0].set_xticklabels(cluster_order, rotation=15, ha="right")

# heart rate per cluster
for i, label in enumerate(cluster_order):
    mask = trainings["cluster_label"] == label
    axes[1].bar(i, trainings.loc[mask, "avg_heart_rate"].mean(),
                color=colors[i])
axes[1].set_title("Avg Heart Rate by Cluster", fontsize=13)
axes[1].set_ylabel("Heart Rate (bpm)")
axes[1].set_xticks(range(K))
axes[1].set_xticklabels(cluster_order, rotation=15, ha="right")

# pace per cluster
for i, label in enumerate(cluster_order):
    mask = trainings["cluster_label"] == label
    axes[2].bar(i, trainings.loc[mask, "pace_min_km"].mean(),
                color=colors[i])
axes[2].set_title("Avg Pace by Cluster", fontsize=13)
axes[2].set_ylabel("Pace (min/km)")
axes[2].set_xticks(range(K))
axes[2].set_xticklabels(cluster_order, rotation=15, ha="right")

plt.suptitle("Cluster Profiles", fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/18_cluster_profiles.png", dpi=150, bbox_inches="tight")
plt.show()

trainings.to_csv("running_clean_with_clusters.csv", index=False)
trainings.to_csv("running_clean_with_clusters_powerbi.csv", index=False, decimal=',')

