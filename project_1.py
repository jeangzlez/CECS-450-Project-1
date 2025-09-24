import glob
import pandas as pd

folder_path = "dataset"
csv_files = glob.glob(folder_path + "/*.csv")

data_frame = pd.DataFrame()
content = []

for filename in csv_files:
    df = pd.read_csv(filename, index_col=None)
    content.append(df)

data_fram = pd.concat(content)
print(data_frame)