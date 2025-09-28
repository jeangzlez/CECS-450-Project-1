import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import os

df = pd.read_csv("dataset/accident.csv")

##-----FILTER DATA AND ANSWER MOST DANGEROUS COMBO QUESTION-----##

# Filter LA County only
la = df[df["COUNTYNAME"] == "LOS ANGELES (37)"]

# Group by road, day, hour, etc.
agg = (la.groupby(["TWAY_ID", "ROUTENAME", "DAY_WEEKNAME", "MONTHNAME", "HOURNAME"])
         ["FATALS"].sum()
         .reset_index()
         .sort_values("FATALS", ascending=False))

# Top 10 result output
print(agg.head(10))

##-----BAR GRAPH VISUALIZATION-----##

# Aggregate fatalities by highway for bar graph
by_hw = (la.groupby("TWAY_ID")["FATALS"]
           .sum()
           .reset_index()
           .sort_values("FATALS", ascending=False)
           .head(10))   # top 10 highways

# Bar Graph Plot
plt.figure(figsize=(10,6))
plt.bar(by_hw["TWAY_ID"], by_hw["FATALS"], color="steelblue")
plt.xticks(rotation=45, ha="right")
plt.xlabel("Street/Highway ID")
plt.ylabel("Total Fatalities (2023)")
plt.title("Top 10 Deadliest Streets/Highways in LA County (2023)")
plt.tight_layout()
plt.show()

##-----INTERACTIVE MAP VISUALIZATION-----##

# Create base map centered on LA
m = folium.Map(location=[34.05, -118.25], zoom_start=9)  # LA center

# Prepare data: only keep rows with valid lat/lon
heat_data = la[["LATITUDE", "LONGITUD", "FATALS"]].dropna()

# Convert to list of points with weight = fatalities
heat_points = heat_data.values.tolist()

# Add heatmap layer
HeatMap(heat_points, radius=10, blur=15, max_zoom=1).add_to(m)

# Save to HTML (open in browser)
m.save("la_fatalities_heatmap.html")
print("Saved interactive map to la_fatalities_heatmap.html")