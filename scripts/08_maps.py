import pandas as pd
import folium
import json
from folium.plugins import MarkerCluster

# --- CONFIG -------------------------------------------------------------------
POINTS_CSV  = "data/processed/route_points.csv"
ROUTES_CSV  = "data/processed/routes.csv"
CLEAN_CSV   = "data/processed/running_clean_with_clusters_powerbi.csv"
OUTPUT_HTML = "dashboard/running_map.html"

CLUSTER_COLORS = {
    "Short & Intense" : "#FF375F",
    "Easy"            : "#0A84FF",
    "Long Run"        : "#30D158",
}

CLUSTER_EMOJIS = {
    "Short & Intense" : "⚡",
    "Easy"            : "🌿",
    "Long Run"        : "🏃",
}

# --- LOAD DATA ----------------------------------------------------------------
points = pd.read_csv(POINTS_CSV)
routes = pd.read_csv(ROUTES_CSV)
clean  = pd.read_csv(CLEAN_CSV, decimal=',')

# --- PREPARE DATES ------------------------------------------------------------
clean["date"]  = pd.to_datetime(clean["datetime"]).dt.date.astype(str)
points["date"] = points["date"].astype(str)
routes["date"] = routes["date"].astype(str)

# --- JOIN CLUSTERS ------------------------------------------------------------
clean_cols = ["date", "cluster_label", "distance_km", "pace_min_km", "year"]
clean_slim = clean[clean_cols]

routes = routes.merge(clean_slim, on="date", how="left")
points = points.merge(clean_slim[["date", "cluster_label"]], on="date", how="left")

# Quitar Treadmill
routes = routes[routes["cluster_label"] != "Treadmill"]
points = points[points["cluster_label"] != "Treadmill"]

# Quitar duplicados por fecha
routes = routes.drop_duplicates(subset=["date"])

# --- STATS --------------------------------------------------------------------
total_routes   = routes["cluster_label"].notna().sum()
total_distance = round(clean["distance_km"].sum())
min_year       = int(clean["year"].min())
max_year       = int(clean["year"].max())

print(f"Ready — {total_routes} routes, {total_distance} km, {min_year}-{max_year}")

# --- BASE MAP -----------------------------------------------------------------
m = folium.Map(
    location=[-12.0964, -77.0020],
    zoom_start=14,
    max_zoom=22,
    tiles=None
)

folium.TileLayer(
    tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attr="Alejandro Ramirez · Running Analysis 2019–2026",
    name="cartodbdarkmatter",
    control=False,
    max_zoom=22
).add_to(m)

# --- LAYER GROUPS -------------------------------------------------------------
marker_clusters = {}
line_groups     = {}

for cluster in CLUSTER_COLORS:
    line_groups[cluster] = folium.FeatureGroup(
        name=f"{CLUSTER_EMOJIS[cluster]} {cluster}", show=True
    )
    mc_options = {
        "maxClusterRadius"        : 120,
        "disableClusteringAtZoom" : 17
    }
    marker_clusters[cluster] = MarkerCluster(options=mc_options)

# --- DRAW ROUTES AND MARKERS --------------------------------------------------
for _, route in routes.iterrows():
    if pd.isna(route["cluster_label"]):
        continue

    cluster = route["cluster_label"]
    color   = CLUSTER_COLORS.get(cluster, "#FFFFFF")
    emoji   = CLUSTER_EMOJIS.get(cluster, "🏃")
    date    = route["date"]

    route_points = points[points["date"] == date]
    if len(route_points) < 2:
        continue

    coords = list(zip(route_points["lat"], route_points["lon"]))

    folium.PolyLine(
        locations=coords,
        color=color,
        weight=2.5,
        opacity=0.5
    ).add_to(line_groups[cluster])

    popup_html = f"""
    <div style="
        font-family: 'Inter', Arial, sans-serif;
        font-size: 12px;
        width: 200px;
        border-radius: 10px;
        overflow: hidden;
    ">
        <div style="
            background: {color};
            padding: 8px 12px;
            color: white;
            font-weight: bold;
            font-size: 13px;
        ">{emoji} {cluster}</div>
        <div style="
            background: #2C2C2E;
            color: white;
            padding: 10px 12px;
            line-height: 1.9;
        ">
            📅 {date}<br>
            📍 {round(route['distance_km'], 2)} km<br>
            ⚡ {round(route['pace_min_km'], 2)} min/km<br>
            📈 {round(route['elevation_gain'], 1)} m gain<br>
            📉 {round(route['elevation_loss'], 1)} m loss
        </div>
    </div>
    """

    folium.CircleMarker(
        location=[route["start_lat"], route["start_lon"]],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=220)
    ).add_to(marker_clusters[cluster])

# --- ADD LAYERS TO MAP --------------------------------------------------------
for cluster in CLUSTER_COLORS:
    marker_clusters[cluster].add_to(line_groups[cluster])
    line_groups[cluster].add_to(m)

# LayerControl nativo oculto — los checkboxes custom lo controlan
folium.LayerControl(position="bottomleft", collapsed=False).add_to(m)

# --- CUSTOM PANEL + JS --------------------------------------------------------
clusters_html = ""
for cluster, color in CLUSTER_COLORS.items():
    emoji = CLUSTER_EMOJIS[cluster]
    safe  = cluster.replace(" ", "_").replace("&", "and")
    clusters_html += f"""
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0;">
            <input
                type="checkbox"
                id="cb_{safe}"
                checked
                style="width:16px; height:16px; accent-color:{color}; cursor:pointer;"
            >
            <span style="color:{color}; font-size:20px;">●</span>
            <span style="font-size:15px;">{emoji} {cluster}</span>
        </div>
    """

panel_html = f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
    .leaflet-control-layers {{
        display: none !important;
    }}
</style>

<div id="panel-left" style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    z-index: 1000;
    background: #2C2C2E;
    border-radius: 14px;
    padding: 24px 28px;
    font-family: 'Inter', Arial, sans-serif;
    color: white;
    width: 280px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.7);
    line-height: 1.6;
">
    <div style="font-size:20px; font-weight:600; color:#30D158; margin-bottom:4px;">
        🏃 Running Map — Lima
    </div>
    <div style="font-size:12px; color:#888; margin-bottom:18px;">
        {total_routes} routes &nbsp;·&nbsp; {total_distance:,} km &nbsp;·&nbsp; {min_year}–{max_year}
    </div>
    <div style="font-size:11px; color:#888; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">
        Session Type
    </div>
    {clusters_html}
    <div style="margin-top:18px; padding-top:14px; border-top:1px solid #3A3A3C; font-size:11px; color:#666;">
        🏠 Indoor sessions not shown
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
    setTimeout(function() {{
        const clusters = {json.dumps(list(CLUSTER_COLORS.keys()))};
        const emojis   = {json.dumps(CLUSTER_EMOJIS)};

        clusters.forEach(function(cluster) {{
            const safe = cluster.replace(/ /g, '_').replace(/&/g, 'and');
            const cb   = document.getElementById('cb_' + safe);
            if (!cb) return;

            cb.addEventListener('change', function() {{
                const label = emojis[cluster] + ' ' + cluster;
                const nativeCbs = document.querySelectorAll(
                    '.leaflet-control-layers-overlays input[type=checkbox]'
                );
                nativeCbs.forEach(function(nativeCb) {{
                    const span = nativeCb.closest('label');
                    if (span && span.textContent.trim().includes(cluster)) {{
                        if (nativeCb.checked !== cb.checked) {{
                            nativeCb.click();
                        }}
                    }}
                }});
            }});
        }});
    }}, 1000);
}});
</script>
"""

m.get_root().html.add_child(folium.Element(panel_html))

# --- SAVE ---------------------------------------------------------------------
m.save(OUTPUT_HTML)
print(f"Map saved to {OUTPUT_HTML}")