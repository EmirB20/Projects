import pandas as pd
import re

url = 'https://fbref.com/en/comps/8/2023-2024/stats/2023-2024-Champions-League-Stats'

# Read table with multi-level headers
tables = pd.read_html(url, attrs={"id": "stats_squads_standard_for"}, header=[0, 1])
df = tables[0]

# Flatten and clean column names
df.columns = [
    re.sub(r'^Unnamed: \d+_level_0\s*', '', ' '.join(col)).strip()
    for col in df.columns
]

# Drop rows where Squad is missing
df = df.dropna(subset=['Squad']).copy()

# Extract country prefix and clean Squad name
df['Country'] = df['Squad'].str.extract(r'^([A-Za-z]{2,3})')  # e.g., 'ENG'
df['Squad'] = df['Squad'].str.replace(r'^[A-Za-z]{2,3}\s+', '', regex=True)

# Move 'Country' column to the front
columns = ['Country'] + [col for col in df.columns if col != 'Country']
df = df[columns]

# Export to CSV
csv_filename = 'champions_league_squad_standard_stats_2023_24.csv'
df.to_csv(csv_filename, index=False)

print(f" Exported successfully to '{csv_filename}'")







