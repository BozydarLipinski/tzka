import pandas as pd

# Sample dataset (replace with your actual dataset)
df = pd.read_csv("old_sector_holdings.csv")

# Step 1: Manual Industry Mapping (for known tickers)
manual_industry_mapping = {
    'GL-PD': 'Financial Services',
    'PTCCY': 'Communication Services',
    'USB-PA': 'Financial Services'
}

# Step 3: Map industries to dataset
for ticker, industry in manual_industry_mapping.items():
    df.loc[df['ticker'] == ticker, 'industry'] = industry

# Step 4: Get unique industries
unique_industries = set(df['industry'])
print("\nUnique Industries Found:\n", unique_industries)

# Step 5: Show tickers with "Unknown" industry
unknown_tickers = df[df['industry'] == 'Unknown']['ticker'].unique()
print("\nTickers with Unknown Industry:\n", unknown_tickers)

print(len(set(df['ticker'])))

print(len(set(df['industry'])))

# Check for missing values in the entire DataFrame
missing_values = df.isnull().sum()

# Print the result
print("Missing values per column:")
print(missing_values)

df.to_csv("old_sector_holdings2.csv", index=False)