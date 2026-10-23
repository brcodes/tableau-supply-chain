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

## Paths
data_dir = "./data/raw"
csv_name = "DataCoSupplyChainDataset.csv"
csv_path =  data_dir + "/" + csv_name
output_dir = "./data/outputs/profiling"
profile_tag = "yprofile"
summary_tag = "yprofile_summary"
csv_name_ = csv_name.replace('.csv', '_csv')

## Profile
df = pd.read_csv(csv_path, encoding="latin-1")
profile = ydata_profiling.ProfileReport(df)

## Pickle
import pickle
with open(output_dir + "/" + csv_name_ + "_" + profile_tag + ".pkl", "wb") as f:
    pickle.dump(profile, f)

## Export 
# Flat csv for Tableau
yprofile_column_stats_to_csv(profile, output_dir + "/" + csv_name_ + "_" + summary_tag + ".csv")
# Full, interactive HTML report
profile.to_file(output_dir + "/" + csv_name_ + "_" + profile_tag + ".html")