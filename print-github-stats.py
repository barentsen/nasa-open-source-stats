import pandas as pd
import numpy as np

df = pd.read_csv("github-api-stats.csv", parse_dates=True)
df['createdAt'] = pd.to_datetime(df['createdAt'])
df['year'] = df['createdAt'].dt.year
df['repo'] = df['repository_owner'].str.cat(df['repository_name'], sep="/")
df['pr_authors'] = df['n_prs_unique_authors']

non_astro_packages = [package.strip() for package in open('non-astro-packages.txt').readlines()]
df = df[~df['repository_name'].isin(non_astro_packages)]
df = df.sort_values(by="n_prs_unique_authors", ascending=False)
df['rank'] = np.arange(1, len(df)+1)
print(df[0:20].to_string(columns=['rank', 'repo', 'pr_authors', 'year'],
                         formatters={'year': lambda x: f'{x:.0f}'},
                         index=False))
