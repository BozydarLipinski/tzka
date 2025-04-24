import pandas as pd

# Load the two datasets
df1 = pd.read_csv("old_processed_aids_data_1.csv")
df2 = pd.read_csv("processed_aids_data_1.csv")

# Strip column names to avoid subtle mismatches
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# Add missing utility columns to df2 with NaN values
for col in ['Utilities_w', 'Utilities_logp']:
    if col not in df2.columns:
        df2[col] = pd.NA

# Align df2 column order to df1
df2 = df2[df1.columns]

# Combine the two datasets
merged_df = pd.concat([df1, df2], ignore_index=True)

# Ensure 'filedFor' is datetime for correct sorting
merged_df['filedFor'] = pd.to_datetime(merged_df['filedFor'], errors='coerce')
merged_df = merged_df.sort_values(by='filedFor')

# Save and inspect
merged_df.to_csv("merged_sector_data_2002_2025.csv", index=False)
print(merged_df.head())
