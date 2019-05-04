import pandas as pd

df = pd.read_csv("repo_opensource_metrics.csv")

non_astro_packages = [package.strip() for package in open('non-astro-packages.txt').readlines()]
repo_name = [part[2] for part in df['github_url'].str.split('/')]

ignore = ~df['exists']
ignore |= [repo in non_astro_packages for repo in repo_name]
df = df[~ignore]

for field in ['readme', 'installation', 'CI', 'docs', 'examples']:
    pct = 100 * df[field].sum() / len(df)
    print(f'Repositories with {field}: {pct:.0f}%')

