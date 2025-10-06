import pandas as pd
import matplotlib.pyplot as plt

#<---------- FILTERING DATA -------->

# read files
df = pd.read_csv("dataset/drimpair.csv")
cf = pd.read_csv("dataset/accident.csv")
sf = pd.read_csv("dataset/drugs.csv")

# filter accident.csv to California only
ca = cf[(cf["STATENAME"] == "CALIFORNIA") | (cf["STATE"] == 6)]

# selected highways in California (from groupmate findings)
highways = ["I-5", "I-10", "I-405", "US-101", "I-110", "I-105", "I-605", "I-710"]
# filters fatal accidents
fatal_acc = ca[ca["TWAY_ID"].isin(highways) & (ca["FATALS"] > 0)]

# finds matching case numbers from csv files
merge_data = fatal_acc.merge(df, on="ST_CASE", how="left")
merge_data = merge_data.merge(sf, on="ST_CASE", how="left")


#<---------- PIECHART PLOT ---------->

# creates a grid that fits 8 piecharts
fig, axes = plt.subplots(4, 2, figsize=(7, 7))
axes = axes.flatten()
# tracks grid to avoid overlaps/rewriting
index = 0

# colors for each slice in piecharts
colors = ['tomato', 'cornflowerblue', 'gold', 'orchid', 'green', 'indianred', 'darkblue']


for hw in highways:
    # filter by highway
    subpies = merge_data[merge_data["TWAY_ID"] == hw]
    if subpies.empty:
        continue

    # tracks type of drug impairments
    counts = subpies["DRIMPAIRNAME"].value_counts().reset_index()
    counts.columns = ["Drug Type", "Count"]

    # design for each piechart/slices
    wedges, texts, autotexts = axes[index].pie(
        counts["Count"],
        startangle=90,
        colors=colors[:len(counts)],
        autopct="%1.1f%%",
        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )

    for autotext in autotexts:
        autotext.set_fontsize(6)

    # title for each piechart
    axes[index].set_title(
        f"{hw}",
        fontsize=10
    )

    # key for piecharts (needed bc too crowded to label directly)
    axes[index].legend(
        wedges,
        counts["Drug Type"],
        title="Drug Impairment Type",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=8,
        title_fontsize=9
    )

    # increment index to avoid revisiting same grid location
    index += 1

# title for entire grid
fig.suptitle("Types of Drug Impairment Reported", fontsize=16)
plt.show()