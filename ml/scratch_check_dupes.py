import pandas as pd
df = pd.read_csv('/Users/arpitatiwari/Desktop/RP/AI-Medical-Symptom-Checker/ml/data/raw/dataset.csv')
print(f"Total rows: {len(df)}")
print(f"Unique rows: {len(df.drop_duplicates())}")
print(df.drop_duplicates()['Disease'].value_counts())
