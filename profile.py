from os import name

import ydata_profiling
import pandas as pd

# Profile to column stats
def yprofile_column_stats_to_csv(profile, output_csv="ydata_column_summary.csv"):
    summary_data = profile.get_description()
    variables = summary_data.variables
    metrics_df = pd.DataFrame.from_dict(variables, orient="index")
    metrics_df.reset_index(inplace=True)
    metrics_df.rename(columns={"index": "column_name"}, inplace=True)
    metrics_df.to_csv(output_csv, index=False)
    
pickle = False

## Paths
data_dir = "./data/raw/"
data_name = "DataCoSupplyChainDataset"
data_type = "csv"
data_ext = "." + data_type
data_file = data_name + data_ext
data_path =  data_dir + "/" + data_file
output_dir = "./data/outputs/profiling/"
profile_name = "yprofile"
summary_name = "yprofile_column_stats"
data_file_nodot = data_name + "_" + data_type

## Profile
df = pd.read_csv(data_path, encoding="latin-1")
profile = ydata_profiling.ProfileReport(df)

## Export
# Pickle
if pickle:
    import pickle
    with open(output_dir + data_file_nodot + "_" + profile_name + ".pkl", "wb") as f:
        pickle.dump(profile, f)
# Flat csv for Tableau
yprofile_column_stats_to_csv(profile, output_dir + data_file_nodot + "_" + summary_name + ".csv")
# Full, interactive HTML report
profile.to_file(output_dir + data_file_nodot + "_" + profile_name + ".html")