import json
import numpy as np
import pandas as pd
import ydata_profiling


# Bulletproof recursive cleaner for complex ydata-profiling data structures
def clean_ydata_object(val):
    if isinstance(val, pd.Series):
        return val.to_dict()
    elif isinstance(val, tuple):
        return [clean_ydata_object(item) for item in val]
    elif isinstance(val, list):
        return [clean_ydata_object(item) for item in val]
    elif isinstance(val, dict):
        return {str(k): clean_ydata_object(v) for k, v in val.items()}
    elif isinstance(val, np.ndarray):
        return val.tolist()
    elif isinstance(val, (np.integer, np.floating)):
        return val.item()
    return val


# Upgraded profile-to-csv function for Tableau
def yprofile_column_stats_to_csv(profile, output_csv="ydata_column_summary.csv"):
    summary_data = profile.get_description()
    variables = summary_data.variables

    summary_rows = []
    counts_rows = []
    hist_rows = []

    for col_name, stats in variables.items():
        # 1. Build scalar/JSON-stringified summary row
        scalar_row = {"column_name": col_name}
        for k, v in stats.items():
            cleaned_v = clean_ydata_object(v)
            if isinstance(cleaned_v, (dict, list)):
                scalar_row[k] = json.dumps(cleaned_v)
            else:
                scalar_row[k] = cleaned_v
        summary_rows.append(scalar_row)

        # 2. Extract Value Counts into a separate long-format table
        for count_key in ["value_counts_without_nan", "value_counts"]:
            if count_key in stats and stats[count_key] is not None:
                val_series = stats[count_key]
                val_dict = (
                    val_series.to_dict()
                    if isinstance(val_series, pd.Series)
                    else val_series
                )
                for val, count in val_dict.items():
                    counts_rows.append({
                        "column_name": col_name,
                        "metric_type": count_key,
                        "value": str(val),
                        "count": int(count) if pd.notna(count) else 0,
                    })

        # 3. Extract Histograms into a separate relational table
        if "histogram" in stats and stats["histogram"] is not None:
            hist_tuple = stats["histogram"]
            if isinstance(hist_tuple, tuple) and len(hist_tuple) == 2:
                counts, bins = hist_tuple
                for i in range(len(counts)):
                    hist_rows.append({
                        "column_name": col_name,
                        "bin_index": i,
                        "bin_start": float(bins[i]),
                        "bin_end": float(bins[i + 1]),
                        "count": int(counts[i]),
                    })

    # Derive secondary paths based on your primary summary filename
    base_path = output_csv.rsplit(".", 1)[0]
    counts_csv = base_path.replace("column_stats", "value_counts") + ".csv"
    hist_csv = base_path.replace("column_stats", "histograms") + ".csv"

    # Save clean CSVs with QUOTE_ALL to prevent parser breaking on text/JSON
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_csv, index=False, quoting=1)

    if counts_rows:
        counts_df = pd.DataFrame(counts_rows)
        counts_df.to_csv(counts_csv, index=False, quoting=1)

    if hist_rows:
        hist_df = pd.DataFrame(hist_rows)
        hist_df.to_csv(hist_csv, index=False, quoting=1)

    print(f"Successfully exported clean Tableau files to directory.")


pickle = False

## Paths
data_dir = "./data/raw/"
data_name = "DataCoSupplyChainDataset"
data_type = "csv"
data_ext = "." + data_type
data_file = data_name + data_ext
data_path = data_dir + "/" + data_file
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

    with open(
        output_dir + data_file_nodot + "_" + profile_name + ".pkl", "wb"
    ) as f:
        pickle.dump(profile, f)

# Flat clean csvs for Tableau (Automatically outputs summary, value_counts, and histograms)
yprofile_column_stats_to_csv(
    profile, output_dir + data_file_nodot + "_" + summary_name + ".csv"
)

# Full, interactive HTML report
profile.to_file(output_dir + data_file_nodot + "_" + profile_name + ".html")