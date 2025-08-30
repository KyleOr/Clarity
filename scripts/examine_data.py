import pandas as pd
import numpy as np

print('=== EXAMINING HOUSEHOLD SPENDING STRUCTURE ===')
df = pd.read_excel('../dataset/household_spending.xlsx')
print(f"Shape: {df.shape}")
for i in range(min(15, len(df))):
    print(f'Row {i}: {df.iloc[i].values}')

print('\n=== EXAMINING HOUSING COST STRUCTURE ===')
df2 = pd.read_excel('../dataset/housing_cost.xlsx')
print(f"Shape: {df2.shape}")
for i in range(min(15, len(df2))):
    print(f'Row {i}: {df2.iloc[i].values}')

print('\n=== EXAMINING INCOME WORK STRUCTURE ===')
df3 = pd.read_excel('../dataset/income_work.xlsx')
print(f"Shape: {df3.shape}")
for i in range(min(15, len(df3))):
    print(f'Row {i}: {df3.iloc[i].values}')
