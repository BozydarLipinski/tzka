import pandas as pd
import numpy as np
import statsmodels.api as sm
import os

# Load dataset
df = pd.read_csv("AIDS_Data.csv")

# Identify share and price columns
share_cols = [col for col in df.columns if col.endswith("_w")]
price_cols = [col for col in df.columns if col.endswith("_logp")]

# Normalize shares to sum to 1
df[share_cols] = df[share_cols].div(df[share_cols].sum(axis=1), axis=0)

# Create output folder
output_dir = "aids_results"
os.makedirs(output_dir, exist_ok=True)

# Loop through each sector to drop
for drop_sector in share_cols:
    shares_used = [col for col in share_cols if col != drop_sector]

    # Prepare independent variables (log prices)
    X = df[price_cols]
    X = sm.add_constant(X)

    # Run OLS for each share equation (excluding dropped sector)
    results = {}
    for share in shares_used:
        y = df[share]
        model = sm.OLS(y, X).fit()
        results[share] = model

    # Compute elasticities
    def compute_elasticities(results, share_cols, price_cols, df, drop_sector):
        elasticities = pd.DataFrame(index=share_cols, columns=price_cols)
        avg_shares = df[share_cols].mean()
        avg_prices = df[price_cols].mean()

        for share in results:
            gamma = results[share].params
            for price in price_cols:
                elasticity = gamma[price] * avg_prices[price] / avg_shares[share]
                elasticities.loc[share, price] = elasticity

        # Enforce adding-up for dropped sector
        elasticities.loc[drop_sector] = -elasticities.drop(drop_sector).sum(axis=0)

        return elasticities

    elasticities = compute_elasticities(results, share_cols, price_cols, df, drop_sector)

    # Save elasticities
    elasticities_file = os.path.join(output_dir, f"elasticities_dropped_{drop_sector}.csv")
    elasticities.to_csv(elasticities_file)

    # Save model stats
    model_stats = []
    for share, model in results.items():
        for param, pval in model.pvalues.items():
            model_stats.append({
                "Dropped": drop_sector,
                "Sector": share,
                "Parameter": param,
                "R-squared": model.rsquared,
                "P-value": pval
            })

    model_stats_df = pd.DataFrame(model_stats)
    stats_file = os.path.join(output_dir, f"model_stats_dropped_{drop_sector}.csv")
    model_stats_df.to_csv(stats_file, index=False)

    print(f"Finished processing with dropped sector: {drop_sector}")
