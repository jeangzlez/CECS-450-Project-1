from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px

#To run python weather_accidents.py
#Make sure correct libraries are installed
CSV = Path("dataset/accident.csv")
df = pd.read_csv(CSV)
df.columns = [c.strip().upper() for c in df.columns]

#Filter LA County
if "STATENAME" in df.columns:
    df = df[df["STATENAME"].astype(str).str.contains("CALIFORNIA", case=False, na=False)]
if "COUNTYNAME" in df.columns:
    df = df[df["COUNTYNAME"].astype(str).str.contains("LOS ANGELES", case=False, na=False)]

#Found highways in la county
road_col = "TWAY_ID" if "TWAY_ID" in df.columns else "ROUTENAME"
if road_col not in df.columns:
    raise ValueError("Expected a road/highway column like TWAY_ID or ROUTENAME")

#Dates
if "DATE" in df.columns:
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
elif {"YEAR","MONTH","DAY"}.issubset(df.columns):
    df["DATE"] = pd.to_datetime(dict(year=df["YEAR"], month=df["MONTH"], day=df["DAY"]), errors="coerce")
else:
    raise ValueError("Need DATE or YEAR/MONTH/DAY columns.")
df = df[df["DATE"].notna()].copy()

#Clean weather csv and flag rain days
if "WEATHERNAME" not in df.columns and "WEATHER" in df.columns:
    code_map = {1:"Clear", 2:"Rain", 3:"Sleet/Hail", 4:"Snow", 5:"Fog/Smog/Smoke", 10:"Cloudy"}
    df["WEATHERNAME"] = df["WEATHER"].map(code_map).fillna("Unknown").astype(str)
else:
    df["WEATHERNAME"] = df["WEATHERNAME"].fillna("Unknown").astype(str).str.title()

df["RAINY"] = df["WEATHERNAME"].str.contains(r"rain|drizzle|shower|thunder", case=False, na=False)
df["WEATHER_GROUP"] = np.where(df["RAINY"], "Rain", "Clear")

#Sort highways in LA
top10 = (df.groupby(road_col)
           .size()
           .reset_index(name="TOTAL_ACCIDENTS")
           .sort_values("TOTAL_ACCIDENTS", ascending=False)
           .head(10))
df = df[df[road_col].isin(top10[road_col])]

#Build daily accident counts per highway
daily = df.groupby([road_col, "DATE"]).size().reset_index(name="ACCIDENTS")
rain_flag = df.groupby(["DATE"])[ "RAINY"].max().reset_index(name="RAINY")
daily = daily.merge(rain_flag, on="DATE", how="left")
daily["DAY_TYPE"] = np.where(daily["RAINY"], "Rain", "Clear")

#Count distinct rain/clear days for normalization
day_counts = daily.groupby(["DAY_TYPE"]).agg(DAYS=("DATE","nunique")).reset_index()

#Per highway, per day-type totals
by_hw_weather = (
    daily.groupby([road_col, "DAY_TYPE"])["ACCIDENTS"].sum().reset_index(name="TOTAL_ACCIDENTS")
)

#Filter out highways without both rain and clear accidents
presence = (
    by_hw_weather.pivot(index=road_col, columns="DAY_TYPE", values="TOTAL_ACCIDENTS")
    .fillna(0)
)
keep_highways = presence[(presence.get("Rain", 0) > 0) & (presence.get("Clear", 0) > 0)].index
by_hw_weather = by_hw_weather[by_hw_weather[road_col].isin(keep_highways)].copy()

#Normalize accidents by number of Rain/Clear days and compute % difference
day_counts_by_type = (
    daily.groupby("DAY_TYPE")["DATE"].nunique().reset_index(name="N_DAYS")
)
day_counts_dict = dict(zip(day_counts_by_type["DAY_TYPE"], day_counts_by_type["N_DAYS"]))

by_hw_weather["ACC_PER_DAY"] = by_hw_weather.apply(
    lambda r: r["TOTAL_ACCIDENTS"] / day_counts_dict.get(r["DAY_TYPE"], 1), axis=1
)
day_counts_by_type = (
    daily.groupby("DAY_TYPE")["DATE"].nunique().reset_index(name="N_DAYS")
)
day_counts_dict = dict(zip(day_counts_by_type["DAY_TYPE"], day_counts_by_type["N_DAYS"]))

by_hw_weather["ACC_PER_DAY"] = by_hw_weather.apply(
    lambda r: r["TOTAL_ACCIDENTS"] / day_counts_dict.get(r["DAY_TYPE"], 1), axis=1
)
pivot = by_hw_weather.pivot(index=road_col, columns="DAY_TYPE", values="ACC_PER_DAY").fillna(0)
pivot["RAIN_VS_CLEAR_DIFF_%"] = (pivot["Rain"] - pivot["Clear"]) / pivot["Clear"] * 100
pivot = pivot.reset_index()

#Build % diff map per highway (safe divide)
pivot["PCT_DIFF"] = np.where(
    pivot["Clear"] > 0,
    (pivot["Rain"] - pivot["Clear"]) / pivot["Clear"] * 100,
    np.nan
)
pct_map = pivot.set_index(road_col)["PCT_DIFF"].to_dict()

#Custom hover feature
def build_hover(row):
    hw = row[road_col]
    day = row["DAY_TYPE"]
    val = row["ACC_PER_DAY"]
    pct = pct_map.get(hw, np.nan)
    if day == "Rain":
        if np.isfinite(pct):
            return (f"<b>{hw}</b><br>{day}: {val:.2f} per day"
                    f"<br>Rain vs Clear: {pct:+.1f}%")
        else:
            return (f"<b>{hw}</b><br>{day}: {val:.2f} per day"
                    f"<br>Rain vs Clear: n/a (no clear baseline)")
    else:
        return f"<b>{hw}</b><br>{day}: {val:.2f} per day<br>(baseline)"

def rain_label(row):
    if row["DAY_TYPE"] != "Rain":
        return ""
    pct = pct_map.get(row[road_col], np.nan)
    return f"{pct:+.0f}%" if np.isfinite(pct) else ""

by_hw_weather["HOVER"] = by_hw_weather.apply(build_hover, axis=1)
by_hw_weather["RAIN_LABEL"] = by_hw_weather.apply(rain_label, axis=1)

fig = px.bar(
    by_hw_weather,
    x=road_col, y="ACC_PER_DAY",
    color="DAY_TYPE", barmode="group",
    color_discrete_map={"Clear":"#ff0000", "Rain":"#1761cf"},
    title="Accidents per Day: Rain vs Clear (Top LA Highways)",
    labels={road_col:"Highway / Street", "ACC_PER_DAY":"Accidents per Day", "DAY_TYPE":"Weather"},
    custom_data=["HOVER", "RAIN_LABEL", "DAY_TYPE"]
)

#Use our custom hover text (no extra trace box)
fig.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")

#Show % label above Rain bars only
fig.update_traces(selector=dict(name="Rain"), texttemplate=None, textposition=None)
fig.update_layout(xaxis_tickangle=-30, hovermode="x unified", margin=dict(t=70))
fig.write_html("la_highway_risk_per_day.html", include_plotlyjs="cdn")
