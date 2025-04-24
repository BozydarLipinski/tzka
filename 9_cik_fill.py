import pandas as pd


def add_mapping_row(df, cik, cusip6, cusip8):
    new_row = pd.DataFrame([{
        'cik': cik,
        'cusip6': cusip6,
        'cusip8': cusip8
    }])
    return pd.concat([df, new_row], ignore_index=True)


df = pd.read_csv("cusip.csv", dtype=str)

df = add_mapping_row(df, "1131399", "37733W", "37733W10")
df = add_mapping_row(df, "929008", "950817", "95081710")
df = add_mapping_row(df, "800921", "641069", "64106940")
df = add_mapping_row(df, "1156039", "49773V", "49773V10")
df = add_mapping_row(df, "1156039", "949773", "949773V1")
df = add_mapping_row(df, "1160497", "G47766", "G4776610")
df = add_mapping_row(df, "1012100", "81217K", "81217K10")
df = add_mapping_row(df, "73309", "670340", "67034010")
df = add_mapping_row(df, "932872", "82028k", "82028k10")
df = add_mapping_row(df, "1026214", "13400 ", "13400 3")
df = add_mapping_row(df, "1199046", "02911 ", "02911 1")
df = add_mapping_row(df, "1013834", "693622", "69362210")

df.to_csv("cusip_V1.csv", index=False)
