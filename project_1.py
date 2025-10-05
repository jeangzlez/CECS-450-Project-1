import pandas as pd
import matplotlib.pyplot as plt

#<---------- FILTERING DATA -------->

# read files
df = pd.read_csv("dataset/drimpair.csv")
cf = pd.read_csv("dataset/accident.csv")

# filter accident.csv to California only
ca = cf[(cf["STATENAME"] == "CALIFORNIA") | (cf["STATE"] == 6)]

# selected highways in California (from groupmate findings)
highways = ["I-5", "I-10", "I-405", "US-101", "I-110", "I-105", "I-605", "I-710"]
# amount of fatal accidents from selected highways
fatal_acc = ca[ca["TWAY_ID"].isin(highways) & (ca["FATALS"] > 0)]
# finds matching case numbers from csv files
match = df[df["ST_CASE"].isin(fatal_acc["ST_CASE"])]

# merges corresponding data from csv files
merged_data = match.merge(fatal_acc[["ST_CASE", "TWAY_ID"]], on="ST_CASE", how="inner")

#<---------- PIECHART PLOT ---------->

# creates a grid that fits 8 piecharts
fig, axes = plt.subplots(2, 4, figsize=(7, 7))
axes = axes.flatten()
# tracks grid to avoid overlaps/rewriting
index = 0

# loops through selected highways
for hw in highways:
    subpies = merged_data[merged_data["TWAY_ID"] == hw]
    if subpies.empty:
        continue

    counts = subpies["DRIMPAIRNAME"].value_counts().reset_index()
    counts.columns = ["Drug Type", "Count"]

    # design for each piechart/slices
    axes[index].pie(
        counts["Count"],
        labels=counts["Drug Type"],
        autopct="%1.1f",
        startangle=90,
        colors=['tomato', 'cornflowerblue', 'gold', 'orchid', 'green', 'indianred', 'darkblue'],
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    # title for each piechart
    axes[index].set_title(f"{hw}")
    # increment index to avoid revisiting same grid location
    index += 1

# title for entire grid
fig.suptitle("Types of Drug Impairment reported")
plt.show()
