import pandas as pd
import requests
import re
import json
from datetime import datetime
import numpy as np
import csv

cusip = {}


with open('cusip_V1.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:  # make sure there's at least two columns
            cusip[row[1]] = row[0]


def remove_until_s(lines):
    for i, line in enumerate(lines):
        if line.lstrip().startswith("<S>"):
            return lines[i + 1:]  # skip the <S> line as well
    return []


# Function to parse a line with fixed-width columns
def parse_fixed_width(line, widths):
    cols = []
    idx = 0
    for width in widths:
        cols.append(line[idx:idx + width].strip())
        idx += width
    return cols


def get_all_txt_links():
    with open('index.json', 'r') as f:
        data = json.load(f)

    return [(filing['periodOfReport'], filing['linkToTxt']) for filing in data.get('filings', []) if
            'linkToTxt' in filing]


def get_column_widths(block):
    positions = []
    for match in re.finditer(r"<[SC]>", block):
        positions.append(match.start())

    # Sort and compute distances (i.e., column widths)
    positions.sort()
    return [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]


def get_company_name(cusip_id):
    if cusip_id in cusip:
        return int(float(cusip[cusip_id]))
    return ""


def retrieve_data_from_url(url, filing_date):
    response = requests.get(url, headers=headers)
    content = response.text

    # Find all <table>...</table> blocks, skipping the first one
    table_blocks = re.findall(r'<TABLE>(?:(?!</TABLE>).)*?CUSIP(?:(?!</TABLE>).)*?</TABLE>', content,
                              re.DOTALL | re.IGNORECASE)

    if not table_blocks:
        return pd.DataFrame()

    data = pd.DataFrame()
    # Process each table block
    processed_rows = []
    for i, table in enumerate(table_blocks):
        lines = table.strip().splitlines()
        lines = remove_until_s(lines)
        for i, line in enumerate(lines):
            if '---' in line:
                lines = lines[:i]  # keep everything before this line
                break

        column_widths = get_column_widths(table)

        # Parse all lines into a dataframe
        parsed_data = [parse_fixed_width(row, column_widths) for row in lines]
        df = pd.DataFrame(parsed_data)
        data = pd.concat([data, df], ignore_index=True)

    for i in range(1, len(data)):
        if data.iloc[i, 2].strip() == "":
            data.iloc[i, 1] = data.iloc[i - 1, 1]
            data.iloc[i, 2] = data.iloc[i - 1, 2]

    mask = ~data.apply(lambda row: row.astype(str).str.contains('---|===')).any(axis=1) & data.iloc[:, 3].fillna(
        '').astype(str).str.strip().ne('')
    data = data[mask]

    try:
        data = data.iloc[:, [2, 3, 4]]
        data['filedFor'] = datetime.fromisoformat(filing_date).date()
        return data
    except:
        return pd.DataFrame()


# MAIN

pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Disable line wrapping
pd.set_option('display.max_colwidth', None)  # Show full content in each cell

headers = {
    "User-Agent": "Your Name (your.email@example.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

txt_links = get_all_txt_links()

all_dfs = []
for url in txt_links:
    data = retrieve_data_from_url(url[1], url[0])
    if not data.empty:
        print(url[0] + '    ' + url[1])
        all_dfs.append(data)

merged_df = pd.concat(all_dfs, ignore_index=True)
merged_df.columns.values[0] = 'cik'
merged_df.columns.values[1] = 'valuation'
merged_df.columns.values[2] = 'shares'

for i in range(len(merged_df)):
    merged_df.at[i, 'cik'] = get_company_name(merged_df.iloc[i]['cik'][:6])


merged_df = merged_df.replace("", np.nan)

merged_df = merged_df.dropna()

merged_df.at[121, 'shares'] = '1,655,125'

merged_df.at[2000, 'valuation'] = merged_df.at[2000, 'valuation'].replace(" 1", "")
merged_df.at[2000, 'shares'] = '120,255,879'

merged_df.at[2014, 'valuation'] = merged_df.at[2014, 'valuation'].replace(" 1", "")
merged_df.at[2014, 'shares'] = '139,945,600'

merged_df.at[3594, 'valuation'] = merged_df.at[3594, 'valuation'].replace(" 1", "")
merged_df.at[3594, 'shares'] = '16,140,300'

merged_df.at[3615, 'valuation'] = merged_df.at[3615, 'valuation'].replace(" 1", "")
merged_df.at[3615, 'shares'] = '12,902,590'

merged_df.at[3603, 'valuation'] = merged_df.at[3603, 'valuation'].replace(" 2", "")
merged_df.at[3603, 'shares'] = '22,000,000'

merged_df.at[4236, 'valuation'] = merged_df.at[4236, 'valuation'].replace(" 2", "")
merged_df.at[4236, 'shares'] = '20,000,000'

merged_df.at[3620, 'valuation'] = merged_df.at[3620, 'valuation'].replace(" 3", "")
merged_df.at[3620, 'shares'] = '38,404,360'


merged_df['filedFor'] = pd.to_datetime(merged_df['filedFor'], errors='coerce')

merged_df = merged_df[~merged_df['filedFor'].dt.year.isin([1998, 1999, 2000, 2001])]

merged_df = merged_df.reset_index(drop=True)

merged_df['valuation'] = merged_df['valuation'].astype(str).replace({'\\$': '', ',': ''}, regex=True)
merged_df['shares'] = merged_df['shares'].astype(str).replace({'\\$': '', ',': ''}, regex=True)

merged_df['cik'] = merged_df['cik'].astype(int)
merged_df['valuation'] = merged_df['valuation'].astype(int)
merged_df['shares'] = merged_df['shares'].astype(int)

merged_df.to_csv("all_data.csv", index=False)