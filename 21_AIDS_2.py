import pandas as pd
import statsmodels.api as sm
import numpy as np


# Load data
df = pd.read_csv("AIDS_DataV1.csv")  # Replace with actual file path

# Identify share and price columns
share_cols = [col for col in df.columns if col.endswith("_w")]
price_cols = [col for col in df.columns if col.endswith("_logp")]

# Compute real income
df["real_income"] = df["portfolio_value"] / df["PPI"]
df["log_real_income"] = np.log(df["real_income"])  # Take log of real income

# Ensure shares sum to 1
df[share_cols] = df[share_cols].div(df[share_cols].sum(axis=1), axis=0)

# Drop one equation to satisfy adding-up constraint
drop_sector = share_cols[-1]  # Dropping last sector
shares_used = [col for col in share_cols if col != drop_sector]

# Prepare independent variables (log prices and log real income)
X = df[price_cols].copy()
X["log_real_income"] = df["log_real_income"]  # Add real income term
X = sm.add_constant(X)  # Adds intercept

# Run OLS for each share equation
results = {}
for share in shares_used:
    y = df[share]  # Dependent variable: budget share
    model = sm.OLS(y, X).fit()  # Fit OLS model
    results[share] = model


# Compute price and income elasticities
def compute_elasticities(results, share_cols, price_cols, df):
    elasticities = pd.DataFrame(index=share_cols, columns=price_cols + ["Income Elasticity"])
    avg_shares = df[share_cols].mean()
    avg_prices = df[price_cols].mean()

    for share in shares_used:
        gamma = results[share].params
        for price in price_cols:
            elasticity = gamma[price] * avg_prices[price] / avg_shares[share]
            elasticities.loc[share, price] = elasticity

        # Compute income elasticity: η_i = 1 + (β_i / avg_share)
        if "log_real_income" in gamma:
            beta_i = gamma["log_real_income"]
            elasticities.loc[share, "Income Elasticity"] = 1 + (beta_i / avg_shares[share])

    # Enforce adding-up constraint for the omitted equation
    elasticities.loc[drop_sector] = -elasticities.sum(axis=0)

    return elasticities


# Compute elasticities
elasticities = compute_elasticities(results, share_cols, price_cols, df)

# Display the results
print("Price and Income Elasticities:")
print(elasticities)

# Save results to CSV
elasticities.to_csv("price_elasticities2.csv", index=True)

# Save R-squared and p-values
model_stats = []
for share, model in results.items():
    for param, pval in model.pvalues.items():
        model_stats.append({
            "Sector": share,
            "Parameter": param,
            "R-squared": model.rsquared,
            "P-value": pval
        })

model_stats_df = pd.DataFrame(model_stats)
model_stats_df.to_csv("model_statistics2.csv", index=False)