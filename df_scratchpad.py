import pandas as pd
df = pd.DataFrame([[1, 2], [4, 5], [7, 8]],
     index=['cobra', 'viper', 'sidewinder'],
     columns=['max_speed', 'shield'])

print(df.loc["viper", "max_speed"])

fruit = "apple"
print(fruit[:-1])
print(df)

if df.empty == True:
    print("equals None")
else:
    print("pizza")