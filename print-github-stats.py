import pandas as pd

df = pd.read_csv("github-api-stats.csv", parse_dates=True)
df['createdAt'] = pd.to_datetime(df['createdAt'])
df['year'] = df['createdAt'].dt.year
df['repo'] = df['repository_owner'].str.cat(df['repository_name'], sep="/")
df['community_size'] = df['n_unique_authors']

non_astro_packages = [package.strip() for package in open('non-astro-packages.txt').readlines()]
df = df[~df['repository_name'].isin(non_astro_packages)]
df = df.sort_values(by="community_size", ascending=False).reset_index()
print(df[0:20].to_string(columns=['repo', 'community_size', 'year'],
                         formatters={'year': lambda x: f'{x:.0f}'}))
