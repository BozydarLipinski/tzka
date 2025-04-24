import pandas as pd
import numpy as np
import statsmodels.api as sm


# Load dataset
df = pd.read_csv("AIDS_Data.csv")  # Replace with actual data file

# Identify share and price columns
share_cols = [col for col in df.columns if col.endswith("_w")]
price_cols = [col for col in df.columns if col.endswith("_logp")]

# Ensure shares sum to 1
df[share_cols] = df[share_cols].div(df[share_cols].sum(axis=1), axis=0)

# Drop one equation to satisfy adding-up constraint
drop_sector = share_cols[-1]
shares_used = [col for col in share_cols if col != drop_sector]

# Prepare independent variables (log prices)
X = df[price_cols]
X = sm.add_constant(X)  # Adds intercept

# Run OLS for each share equation
results = {}
for share in shares_used:
    y = df[share]
    model = sm.OLS(y, X).fit()
    results[share] = model


# Compute price elasticities
def compute_elasticities(results, share_cols, price_cols, df):
    elasticities = pd.DataFrame(index=share_cols, columns=price_cols)
    avg_shares = df[share_cols].mean()
    avg_prices = df[price_cols].mean()

    for share in shares_used:
        gamma = results[share].params
        for price in price_cols:
            elasticity = gamma[price] * avg_prices[price] / avg_shares[share]
            elasticities.loc[share, price] = elasticity

    # Enforce adding-up constraint for the omitted equation
    elasticities.loc[drop_sector] = -elasticities.sum(axis=0)

    return elasticities


elasticities = compute_elasticities(results, share_cols, price_cols, df)

# Display the table
print("Price Elasticities:")
print(elasticities)

# Save results to CSV
elasticities.to_csv("price_elasticities1.csv", index=True)


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
model_stats_df.to_csv("model_statistics1.csv", index=False)