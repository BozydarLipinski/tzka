import pandas as pd
import requests


# Your FRED API Key
API_KEY = "ddcbc5b85ee9c087693da84886d208bc"
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Define the FRED series ID you want to fetch (e.g., GDP, interest rate, etc.)
SERIES_ID = "PPIACO"

# Load your dataset (ensure it has a 'date' column in YYYY-MM-DD format)
df = pd.read_csv("AIDS_Data.csv")

# Convert 'date' column to datetime format
df["filedFor"] = pd.to_datetime(df["filedFor"]).dt.strftime("%Y-%m-%d")


# Function to fetch FRED data for a given date
def get_fred_data(date):
    params = {
        "series_id": SERIES_ID,
        "api_key": API_KEY,
        "file_type": "json",
        "observation_start": date,
        "observation_end": date,
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json().get("observations", [])
        return float(data[0]["value"]) if data else None
    else:
        print(f"Error fetching data for {date}: {response.status_code}")
        return None


# Fetch FRED data for each date in the dataset
df["PPI"] = df["filedFor"].apply(get_fred_data)

# Save the updated dataset
df.to_csv("AIDS_DataV1.csv", index=False)
print("Data saved to AIDS_DataV1.csv")