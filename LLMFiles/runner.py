
import pandas as pd

df = pd.read_csv("sales_data.csv")

df_2024 = df[df['year'] == 2024]

df_filtered = df_2024[df_2024['sales'] > 10000]

median_profit = df_filtered['profit'].median()

print(round(median_profit))
