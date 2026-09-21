import pandas as pd


def add_col(data):
    file = 'kwork.xlsx'
    new_row = pd.DataFrame([data])
    existing = pd.read_excel(file, sheet_name='data')
    df = pd.concat([existing, new_row], ignore_index=True)
    df.to_excel(file, sheet_name='data', index=False)

