import pandas as pd
import statsmodels.api as sm
import numpy as np
import os

# Load data
df = pd.read_csv("AIDS_DataV1.csv")

# Identify share and price columns
share_cols = [col for col in df.columns if col.endswith("_w")]
price_cols = [col for col in df.columns if col.endswith("_logp")]

# Compute log real income
df["real_income"] = df["portfolio_value"] / df["PPI"]
df["log_real_income"] = np.log(df["real_income"])

# Normalize shares
df[share_cols] = df[share_cols].div(df[share_cols].sum(axis=1), axis=0)

# Output directory
output_dir = "aids_income_results"
os.makedirs(output_dir, exist_ok=True)

# Loop over sectors to drop each one
for drop_sector in share_cols:
    shares_used = [col for col in share_cols if col != drop_sector]

    # Independent variables
    X = df[price_cols].copy()
    X["log_real_income"] = df["log_real_income"]
    X = sm.add_constant(X)

    # Run OLS for each share (except dropped)
    results = {}
    for share in shares_used:
        y = df[share]
        model = sm.OLS(y, X).fit()
        results[share] = model

    # Compute elasticities
    def compute_elasticities(results, share_cols, price_cols, df, drop_sector):
        cols = price_cols + ["Income Elasticity"]
        elasticities = pd.DataFrame(index=share_cols, columns=cols)
        avg_shares = df[share_cols].mean()
        avg_prices = df[price_cols].mean()

        for share in results:
            gamma = results[share].params
            for price in price_cols:
                elasticity = gamma[price] * avg_prices[price] / avg_shares[share]
                elasticities.loc[share, price] = elasticity

            if "log_real_income" in gamma:
                beta_i = gamma["log_real_income"]
                elasticities.loc[share, "Income Elasticity"] = 1 + (beta_i / avg_shares[share])

        # Add dropped sector using adding-up
        elasticities.loc[drop_sector] = -elasticities.drop(drop_sector).sum(axis=0)

        return elasticities

    elasticities = compute_elasticities(results, share_cols, price_cols, df, drop_sector)

    # Save elasticities
    elasticities_file = os.path.join(output_dir, f"elasticities_income_dropped_{drop_sector}.csv")
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

    stats_file = os.path.join(output_dir, f"model_stats_income_dropped_{drop_sector}.csv")
    pd.DataFrame(model_stats).to_csv(stats_file, index=False)

    print(f"Completed: dropped {drop_sector}")

