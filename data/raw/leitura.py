import pandas as pd

df = pd.read_csv("raw/Demonstrativo Fecap v3.csv", encoding="latin1")

print("Linhas e colunas:", df.shape)

print("\nColunas:")
print(df.columns.tolist())

print("\nTipos de dados:")
print(df.dtypes)

print("\nValores nulos:")
print(df.isnull().sum())

print("\nPrimeiras linhas:")
print(df.head())