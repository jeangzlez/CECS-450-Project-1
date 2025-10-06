# generates bar chart, trend lines, and an interactive folium map for:
# I-5, I-10, I-405, US-101, I-110, I-105, I-605, I-710

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

# Configuration
YEARS = list(range(2018, 2024))
TARGET_FREEWAYS = {"I-5", "I-10", "I-405", "US-101", "I-110", "I-105", "I-605", "I-710"}
MAP_CENTER = [34.05, -118.25]   # los Angeles
HEAT_RADIUS = 20            
HEAT_BLUR = 28
HEAT_MIN_OPACITY = 0.55
MARKERS_PER_FREEWAY = 1200     

# load & preprocess data
base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "heat_map_data")
out_dir = os.path.join(base_dir, "outputs")
os.makedirs(out_dir, exist_ok=True)

dfs = []
for y in YEARS:
    p = os.path.join(data_dir, f"accident{y}.csv")
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing file: {p}")
    df_y = pd.read_csv(p, encoding="latin1", low_memory=False)
    if "YEAR" not in df_y.columns:
        df_y["YEAR"] = y
    dfs.append(df_y)

df = pd.concat(dfs, ignore_index=True)

for col in ["FATALS", "LATITUDE", "LONGITUD", "YEAR"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Focus on Los Angeles County
la = df[df["COUNTYNAME"] == "LOS ANGELES (37)"].copy()

def normalize_freeway(s: str) -> str | None:
    """Extract base freeway code (I-5, US-101, ...) from TWAY_ID variants.
       Returns None if not one of our 8 targets.
    """
    if not isinstance(s, str):
        return None
    s = s.strip().upper()
    m = re.match(r'^(I-\d+|US-\d+|SR-\d+)\b', s)
    if not m:
        return None
    base = m.group(1)
    return base if base in TARGET_FREEWAYS else None

la["FREEWAY_BASE"] = la["TWAY_ID"].map(normalize_freeway)
major = la[la["FREEWAY_BASE"].notna()].copy()

print("Loaded rows LA (2018–2023):", len(la))
print("Year counts (LA):\n", la["YEAR"].value_counts().sort_index())
print("\nRows on target freeways (LA):", len(major))
print(major["FREEWAY_BASE"].value_counts(), "\n")

# Aggregate tables
# Total fatalities per freeway
by_fw_all = (
    major.groupby("FREEWAY_BASE")["FATALS"]
         .sum()
         .reset_index()
         .sort_values("FATALS", ascending=False)
)

# Yearly trend per freeway (pivoted)
trend = (
    major.groupby(["YEAR", "FREEWAY_BASE"])["FATALS"]
         .sum()
         .reset_index()
         .pivot(index="YEAR", columns="FREEWAY_BASE", values="FATALS")
         .fillna(0)
         .astype(int)
)

# Top 5 deadliest combos of freeway + day of week + month + hour
agg8 = (
    major.groupby(["FREEWAY_BASE", "DAY_WEEKNAME", "MONTHNAME", "HOURNAME"])["FATALS"]
         .sum()
         .reset_index()
         .sort_values("FATALS", ascending=False)
)

print("Top 5 deadliest combos among the 8 freeways:")
print(agg8.head(5), "\n")

# Save tables
by_fw_all.to_csv(os.path.join(out_dir, "top_freeways_2018_2023.csv"), index=False)
trend.to_csv(os.path.join(out_dir, "trend_table_2018_2023.csv"))
agg8.head(20).to_csv(os.path.join(out_dir, "deadliest_combos_top20.csv"), index=False)


plt.figure(figsize=(10, 6))
plt.bar(by_fw_all["FREEWAY_BASE"], by_fw_all["FATALS"])
plt.xlabel("Freeway")
plt.ylabel("Total Fatalities (2018–2023)")
plt.title("Deadliest Major Freeways in LA County (2018–2023)")
plt.tight_layout()
plt.show()

# Trend lines per freeway
trend_long = (
    major.groupby(["YEAR", "FREEWAY_BASE"])["FATALS"]
         .sum()
         .reset_index()
)

plt.figure(figsize=(10, 6))
for fw in sorted(trend_long["FREEWAY_BASE"].unique()):
    sub = trend_long[trend_long["FREEWAY_BASE"] == fw]
    plt.plot(sub["YEAR"], sub["FATALS"], marker="o", label=fw)
plt.xlabel("Year")
plt.ylabel("Fatalities")
plt.title("Fatalities by Freeway (2018–2023)")
plt.legend()
plt.tight_layout()
plt.show()

# Interactive folium map
m = folium.Map(location=MAP_CENTER, zoom_start=9, tiles="cartodb positron")

# Overall heat layer
heat_all = major[["LATITUDE", "LONGITUD", "FATALS"]].dropna()
fg_all = folium.FeatureGroup(name="All Freeways (Heatmap, 2018–2023)", show=True)
HeatMap(
    heat_all[["LATITUDE", "LONGITUD", "FATALS"]].values.tolist(),
    radius=HEAT_RADIUS, blur=HEAT_BLUR, min_opacity=HEAT_MIN_OPACITY
).add_to(fg_all)
fg_all.add_to(m)

# Per year heat layers
for y in YEARS:
    sub = major[(major["YEAR"] == y)][["LATITUDE", "LONGITUD", "FATALS"]].dropna()
    if sub.empty:
        continue
    fg = folium.FeatureGroup(name=f"Heatmap {y}", show=False)
    HeatMap(
        sub[["LATITUDE", "LONGITUD", "FATALS"]].values.tolist(),
        radius=HEAT_RADIUS, blur=HEAT_BLUR, min_opacity=HEAT_MIN_OPACITY
    ).add_to(fg)
    fg.add_to(m)

# Per freeway marker layers with tooltips/popups
colors = {
    "I-5": "red", "I-10": "blue", "I-405": "green", "US-101": "purple",
    "I-110": "orange", "I-105": "pink", "I-605": "brown", "I-710": "teal"
}

for fw, col in colors.items():
    layer = folium.FeatureGroup(name=f"{fw} (markers)", show=False)
    fw_df = major[major["FREEWAY_BASE"] == fw].dropna(subset=["LATITUDE", "LONGITUD"])

    if len(fw_df) > MARKERS_PER_FREEWAY:
        fw_df = fw_df.sample(MARKERS_PER_FREEWAY, random_state=42)

    for _, row in fw_df.iterrows():
        tooltip = f"{fw} — {row.get('HOURNAME', '')}, {row.get('MONTHNAME', '')}, {int(row.get('YEAR', 0))}"
        popup = folium.Popup(
            html=(
                f"<b>Freeway:</b> {fw}<br>"
                f"<b>Date/Time:</b> {row.get('DAY_WEEKNAME','')} / "
                f"{row.get('MONTHNAME','')} / {row.get('HOURNAME','')} / {int(row.get('YEAR', 0))}<br>"
                f"<b>Fatalities:</b> {int(row.get('FATALS', 0))}"
            ),
            max_width=280
        )
        folium.CircleMarker(
            location=[row["LATITUDE"], row["LONGITUD"]],
            radius=4 + int(row.get("FATALS", 1)),
            color=col, fill=True, fill_opacity=0.6,
            tooltip=tooltip, popup=popup
        ).add_to(layer)
    layer.add_to(m)

# legend
legend_html = """<div style="position: fixed; bottom: 50px; left: 50px; width: 180px;
background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding:6px">
<b>Freeways</b><br>
<i style="background:red;width:10px;height:10px;display:inline-block"></i>&nbsp;I-5<br>
<i style="background:blue;width:10px;height:10px;display:inline-block"></i>&nbsp;I-10<br>
<i style="background:green;width:10px;height:10px;display:inline-block"></i>&nbsp;I-405<br>
<i style="background:purple;width:10px;height:10px;display:inline-block"></i>&nbsp;US-101<br>
<i style="background:orange;width:10px;height:10px;display:inline-block"></i>&nbsp;I-110<br>
<i style="background:pink;width:10px;height:10px;display:inline-block"></i>&nbsp;I-105<br>
<i style="background:brown;width:10px;height:10px;display:inline-block"></i>&nbsp;I-605<br>
<i style="background:teal;width:10px;height:10px;display:inline-block"></i>&nbsp;I-710
</div>"""
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl(collapsed=False).add_to(m)

out_map = os.path.join(base_dir, "interactive_major_freeways_2018_2023.html")
m.save(out_map)
print(f"Saved {out_map}")
