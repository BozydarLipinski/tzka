import pandas as pd


dane = pd.read_csv("AIDS_DataV1.csv")
wyniki = pd.read_csv("price_elasticities2.csv")
statystyki = pd.read_csv("model_statistics2.csv")

dane.to_excel("AIDS_Data.xlsx", index= False, engine='openpyxl')

wyniki.to_excel("Model_Results.xlsx", index= False, engine='openpyxl')

statystyki.to_excel("Model_Statistics.xlsx", index= False, engine='openpyxl')