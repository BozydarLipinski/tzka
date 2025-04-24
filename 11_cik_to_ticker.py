import pandas as pd
from sec_cik_mapper import StockMapper

# Load the cleaned DataFrame
df = pd.read_csv('all_data.csv')

# Initialize the mapper
mapper = StockMapper()

# Convert CIK to string and pad with leading zeros
df['cik'] = df['cik'].astype(str).str.zfill(10)

df = df.rename(columns={
    'valuation': 'value',
    'shares': 'no_shares'
})

# Convert 'value' to numeric (in case it's still string) and multiply by 1000
df['value'] = pd.to_numeric(df['value']) * 1000


# Map CIKs to tickers
df['ticker'] = df['cik'].apply(lambda cik: mapper.cik_to_tickers.get(cik))
df['ticker'] = df['ticker'].apply(lambda tickers: list(tickers)[0] if tickers else None)

df = df.groupby(["filedFor", "cik", "ticker"], as_index=False).agg({
    "no_shares": "sum",
    "value": "sum"
})

df.to_csv("old_data.csv", index=False)