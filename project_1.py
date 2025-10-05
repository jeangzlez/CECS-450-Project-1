import pandas as pd
import matplotlib.pyplot as plt

# read files
df = pd.read_csv("dataset/drimpair.csv")
cf = pd.read_csv("dataset/accident.csv")

# filter to California only
ca = cf[(cf["STATENAME"] == "CALIFORNIA") | (cf["STATE"] == 6)]

# highways selected from groupmate's findings
highways = ["I-5", "I-10", "I-405", "US-101", "I-110", "I-105", "I-605", "I-710"]
# checks amount of fatalities in highways
fatal_acc = ca[ca["TWAY_ID"].isin(highways) & (ca["FATALS"] > 0)]
# matches case number from diff csv files
match = df[df["ST_CASE"].isin(fatal_acc["ST_CASE"])]

# merges corresponding data from csv files
merged_data = match.merge(fatal_acc[["ST_CASE", "TWAY_ID"]], on="ST_CASE", how="inner")

# piecharts
for hw in highways:
    subpies = merged_data[merged_data["TWAY_ID"] == hw]
    if subpies.empty:
        continue
    counts = subpies["DRIMPAIRNAME"].value_counts().reset_index()
    counts.columns = ["Drug Type", "Count"]

    # customization for piecharts
    plt.figure(figsize=(7, 7))
    plt.pie(
        counts["Count"],
        labels=counts["Drug Type"],
        autopct="%1.1f%%",
        startangle=90,
        textprops={'fontsize': 11},
        colors=['tomato', 'cornflowerblue', 'gold', 'orchid', 'green', 'indianred', 'darkblue' ],
        wedgeprops={'edgecolor': 'white', 'linewidth': 3}
    )


    plt.title(
        #f"Drug Impairment in Fatal Accidents on {hw}"
        f"{hw}",
        fontdict={"fontsize": 18},
        pad=20
    )
    plt.show()