"""Script to print arXiv identifiers of papers given an ADS query.

For this to work, you need to `pip install ads` and also make sure
to store your ADS developer key in `~/.ads/dev_key `.
You can get an ADS key from https://ui.adsabs.harvard.edu/user/settings/token.
"""
import ads

qry = ads.SearchQuery(q="full:'github.com' Kepler",
                      fl=['identifier', 'citation_count'],
                      rows=9999999999)
for paper in qry:
    for identifier in paper.identifier:
        if 'arXiv:' in identifier:
            print(f"{identifier},{paper.citation_count}")
